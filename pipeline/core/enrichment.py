"""
enrichment.py — AI-powered enrichment for hackathons with stub data.

Finds hackathons with:
  1. registration_close = 2099-12-31 (stub deadline from list-view scrapers)
  2. Missing or very short longDescription

For each, scrapes the actual applyUrl page, extracts text, and uses
Mistral AI to parse out:
  - The real registration deadline
  - A comprehensive long description (problem statement, prizes, eligibility, etc.)

This is run as a pipeline phase AFTER upserts but BEFORE status_sweep,
so the sweep can correctly calculate status from real dates.
"""
import os
import json
import httpx
from datetime import datetime, timezone
from bs4 import BeautifulSoup

from dotenv import load_dotenv
load_dotenv()

MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY", "").strip().strip('"').strip("'")
MISTRAL_MODEL = "mistral-small-latest"
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"

MAX_ENRICH_PER_RUN = 25  # Don't burn too many API calls per pipeline run


def _fetch_page_text(url: str) -> str | None:
    """Fetch the URL and return clean body text (no HTML)."""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        with httpx.Client(timeout=20, follow_redirects=True, headers=headers) as client:
            r = client.get(url)
            if r.status_code >= 400:
                print(f"[enrichment] HTTP {r.status_code} for {url}")
                return None
            soup = BeautifulSoup(r.text, "html.parser")

            # Remove script/style/nav/header/footer noise
            for tag in soup(["script", "style", "nav", "header", "footer", "noscript", "svg", "img"]):
                tag.decompose()

            text = soup.get_text(separator="\n", strip=True)
            # Collapse whitespace
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            clean = "\n".join(lines)
            # Cap at ~6000 chars to stay within context window
            return clean[:6000] if clean else None
    except Exception as e:
        print(f"[enrichment] Failed to fetch {url}: {e}")
        return None


def _call_mistral(page_text: str, title: str) -> dict | None:
    """Call Mistral API to extract structured hackathon data from page text."""
    if not MISTRAL_API_KEY:
        print("[enrichment] No MISTRAL_API_KEY set, skipping enrichment")
        return None

    system_prompt = """You are a hackathon data extraction assistant. Given the text content of a hackathon page, extract the following fields accurately. Return ONLY valid JSON, no markdown, no explanation.

JSON schema:
{
  "registration_deadline": "YYYY-MM-DD or null if not found",
  "event_start": "YYYY-MM-DD or null",
  "event_end": "YYYY-MM-DD or null",
  "long_description": "A comprehensive 3-5 paragraph description covering: what the hackathon is about, problem statement/tracks, prizes breakdown, eligibility criteria, team requirements, schedule/format, and any notable sponsors. Write in third person. 800-2000 characters.",
  "prize_pool": number or null,
  "prize_currency": "USD" or "INR" or null,
  "prize_description": "Brief prize breakdown e.g. '1st: $5000, 2nd: $2500, 3rd: $1000' or null",
  "team_size_min": number or null,
  "team_size_max": number or null,
  "mode": "ONLINE" or "OFFLINE" or "HYBRID" or null,
  "eligibility": "STUDENTS" or "OPEN" or "PROFESSIONALS" or null,
  "organizer_name": "string or null",
  "theme_tags": ["tag1", "tag2"] (max 5 tags)
}

Important rules:
- For dates: Use the CURRENT or NEXT occurrence. Today's date context is provided.
- For registration_deadline: Look for "registration closes", "apply by", "deadline", "submissions due", "last date" etc.
- If the page says the hackathon has ended or registrations are closed, set registration_deadline to a past date.
- For long_description: Write a thorough, informative summary. Do NOT just copy the title. Include all available details about tracks, prizes, format, who can participate.
- prize_pool should be the TOTAL prize amount as a number, not a string.
- Return ONLY the JSON object, nothing else."""

    user_prompt = f"""Today's date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}
Hackathon title: {title}

Page content:
{page_text}"""

    try:
        with httpx.Client(timeout=30) as client:
            r = client.post(
                MISTRAL_URL,
                headers={
                    "Authorization": f"Bearer {MISTRAL_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": MISTRAL_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.1,
                    "max_tokens": 2000,
                },
            )
            if r.status_code != 200:
                print(f"[enrichment] Mistral API error: {r.status_code} {r.text[:200]}")
                return None

            data = r.json()
            content = data["choices"][0]["message"]["content"].strip()

            # Strip markdown code fences if present
            if content.startswith("```"):
                content = content.split("\n", 1)[1] if "\n" in content else content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()

            return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"[enrichment] Failed to parse Mistral response as JSON: {e}")
        return None
    except Exception as e:
        print(f"[enrichment] Mistral call failed: {e}")
        return None


def run_enrichment(supabase_client) -> dict:
    """
    Main entry point. Finds stub hackathons, enriches them via AI, updates DB.
    Returns summary dict.
    """
    summary = {"enriched": 0, "skipped": 0, "errors": 0}

    if not MISTRAL_API_KEY:
        print("[enrichment] MISTRAL_API_KEY not set — skipping enrichment phase")
        return summary

    # Find hackathons needing enrichment:
    # 1. Stub deadline (2099-12-31)
    # 2. OR missing/very short longDescription (< 100 chars)
    try:
        # Fetch hackathons with stub deadlines
        stub_response = supabase_client.table("Hackathon").select(
            "id, title, applyUrl, registrationClose, longDescription, description, source, organizerName"
        ).eq("registrationClose", "2099-12-31T00:00:00+00:00").limit(MAX_ENRICH_PER_RUN).execute()

        stub_rows = stub_response.data or []

        # Also fetch ones with missing longDescription that aren't stub-dated
        short_desc_response = supabase_client.table("Hackathon").select(
            "id, title, applyUrl, registrationClose, longDescription, description, source, organizerName"
        ).is_("longDescription", "null").neq(
            "registrationClose", "2099-12-31T00:00:00+00:00"
        ).in_("status", ["OPEN", "CLOSING_SOON", "UPCOMING"]).limit(
            MAX_ENRICH_PER_RUN
        ).execute()

        short_rows = short_desc_response.data or []

        # Combine and deduplicate
        seen_ids = set()
        rows = []
        for row in stub_rows + short_rows:
            if row["id"] not in seen_ids:
                seen_ids.add(row["id"])
                rows.append(row)

        rows = rows[:MAX_ENRICH_PER_RUN]

    except Exception as e:
        print(f"[enrichment] Failed to query hackathons: {e}")
        summary["errors"] += 1
        return summary

    if not rows:
        print("[enrichment] No hackathons need enrichment")
        return summary

    print(f"[enrichment] Found {len(rows)} hackathons to enrich")

    for row in rows:
        title = row.get("title", "?")
        url = row.get("applyUrl", "")
        hackathon_id = row["id"]

        print(f"[enrichment] Enriching: {title[:60]}...")

        # Step 1: Fetch page text
        page_text = _fetch_page_text(url)
        if not page_text or len(page_text) < 100:
            print(f"[enrichment]   Skipped (no usable page text)")
            summary["skipped"] += 1
            continue

        # Step 2: Call Mistral
        extracted = _call_mistral(page_text, title)
        if not extracted:
            print(f"[enrichment]   Skipped (AI extraction failed)")
            summary["skipped"] += 1
            continue

        # Step 3: Build update payload
        update = {}
        now = datetime.now(timezone.utc).isoformat()
        update["updatedAt"] = now

        # Update deadline if we got a real one
        deadline = extracted.get("registration_deadline")
        if deadline and deadline != "null" and len(deadline) == 10:
            try:
                # Validate the date
                from datetime import date
                parsed = date.fromisoformat(deadline)
                update["registrationClose"] = f"{deadline}T00:00:00+00:00"
                print(f"[enrichment]   Deadline: {deadline}")
            except ValueError:
                pass

        # Update event dates
        event_start = extracted.get("event_start")
        if event_start and event_start != "null" and len(event_start) == 10:
            try:
                from datetime import date
                date.fromisoformat(event_start)
                update["eventStart"] = f"{event_start}T00:00:00+00:00"
            except ValueError:
                pass

        event_end = extracted.get("event_end")
        if event_end and event_end != "null" and len(event_end) == 10:
            try:
                from datetime import date
                date.fromisoformat(event_end)
                update["eventEnd"] = f"{event_end}T00:00:00+00:00"
            except ValueError:
                pass

        # Update long description
        long_desc = extracted.get("long_description")
        if long_desc and isinstance(long_desc, str) and len(long_desc) > 100:
            update["longDescription"] = long_desc[:5000]
            # Also update short description if current one is very short
            current_desc = row.get("description") or ""
            if len(current_desc) < 100:
                update["description"] = long_desc[:1000]
            print(f"[enrichment]   Description: {len(long_desc)} chars")

        # Update prize info if missing
        prize = extracted.get("prize_pool")
        if prize and isinstance(prize, (int, float)) and prize > 0:
            update["prizePool"] = prize
            if extracted.get("prize_currency"):
                update["prizeCurrency"] = extracted["prize_currency"]

        prize_desc = extracted.get("prize_description")
        if prize_desc and isinstance(prize_desc, str):
            update["prizeDescription"] = prize_desc[:500]

        # Update team sizes if found
        if extracted.get("team_size_min") and isinstance(extracted["team_size_min"], int):
            update["teamSizeMin"] = extracted["team_size_min"]
        if extracted.get("team_size_max") and isinstance(extracted["team_size_max"], int):
            update["teamSizeMax"] = extracted["team_size_max"]

        # Update mode if found
        mode = extracted.get("mode")
        if mode in ("ONLINE", "OFFLINE", "HYBRID"):
            update["mode"] = mode

        # Update eligibility if found
        elig = extracted.get("eligibility")
        if elig in ("STUDENTS", "OPEN", "PROFESSIONALS"):
            update["eligibility"] = elig

        # Update organizer name if found and current is generic
        org = extracted.get("organizer_name")
        current_org = row.get("organizerName", "")
        generic_orgs = {"Devpost", "DoraHacks", "HackerEarth", "HackerRank", "Unstop", "Hack2Skill", "Luma Host"}
        if org and isinstance(org, str) and len(org) > 2:
            if current_org in generic_orgs or len(current_org) < 3:
                update["organizerName"] = org[:255]

        # Update tags
        tags = extracted.get("theme_tags")
        if tags and isinstance(tags, list) and len(tags) > 0:
            clean_tags = [str(t).strip() for t in tags if isinstance(t, str) and 2 < len(t.strip()) < 60][:8]
            if clean_tags:
                update["themeTags"] = clean_tags

        # Step 4: Apply update
        if len(update) > 1:  # more than just updatedAt
            try:
                supabase_client.table("Hackathon").update(update).eq("id", hackathon_id).execute()
                summary["enriched"] += 1
                print(f"[enrichment]   OK Updated {len(update)-1} fields")
            except Exception as e:
                print(f"[enrichment]   FAIL DB update failed: {e}")
                summary["errors"] += 1
        else:
            summary["skipped"] += 1
            print(f"[enrichment]   Skipped (no new data extracted)")

    print(f"[enrichment] Done: {summary['enriched']} enriched, {summary['skipped']} skipped, {summary['errors']} errors")
    return summary
