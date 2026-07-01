"""
devpost.py — Devpost connector.
Uses the undocumented Devpost JSON API — much faster and WAF-safe vs Playwright.
Falls back to Playwright if the API changes.
"""
import re

import httpx

from .base import BaseConnector, ConnectorResult, RawHackathon

API_URL = "https://devpost.com/api/hackathons?challenge_type[]=online&status[]=open&status[]=upcoming&page={page}&per_page=24"

UA = "Mozilla/5.0 (compatible; 1ph-bot/1.0)"


def _clean_prize(text: str):
    """Extract float prize from a possibly HTML-containing string."""
    if not text:
        return None
    # Strip HTML tags
    clean = re.sub(r"<[^>]+>", "", text)
    clean = clean.replace(",", "").replace("$", "").strip()
    nums = re.findall(r"\d+(?:\.\d+)?", clean)
    if nums:
        try:
            return float(nums[0])
        except ValueError:
            pass
    return None


def _parse_date(date_str: str):
    """Parse dates like 'May 19 - Aug 17, 2026' to extract end date."""
    if not date_str:
        return None
    import re
    # Look for a final date pattern
    months = {
        "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05",
        "jun": "06", "jul": "07", "aug": "08", "sep": "09", "oct": "10",
        "nov": "11", "dec": "12"
    }
    # Try to extract the end date (second date after dash)
    parts = re.split(r"\s*-\s*", date_str)
    target = parts[-1].strip() if len(parts) > 1 else parts[0].strip()
    m = re.search(r"(\w{3})\w*\s+(\d+),?\s*(\d{4})", target, re.IGNORECASE)
    if m:
        mon = months.get(m.group(1).lower(), "01")
        day = m.group(2).zfill(2)
        year = m.group(3)
        return f"{year}-{mon}-{day}"
    return None


class DevpostConnector(BaseConnector):
    SOURCE = "DEVPOST"
    SCOPE = "GLOBAL"

    def fetch(self) -> ConnectorResult:
        records = []
        error = None

        try:
            with httpx.Client(
                timeout=25,
                follow_redirects=True,
                headers={
                    "User-Agent": UA,
                    "Accept": "application/json",
                    "Referer": "https://devpost.com/hackathons",
                }
            ) as client:
                page = 1
                max_pages = 12
                seen: set = set()

                while page <= max_pages:
                    url = API_URL.format(page=page)
                    try:
                        r = client.get(url)
                        if r.status_code != 200:
                            print(f"[{self.SOURCE}] HTTP {r.status_code} on page {page}, stopping")
                            break
                        data = r.json()
                    except Exception as e:
                        print(f"[{self.SOURCE}] Request error on page {page}: {e}")
                        break

                    hackathons = data.get("hackathons", [])
                    if not hackathons:
                        break

                    for h in hackathons:
                        try:
                            hid = str(h.get("id", ""))
                            if not hid or hid in seen:
                                continue
                            seen.add(hid)

                            title = h.get("title", "").strip()
                            if not title:
                                continue

                            apply_url = h.get("url", "").strip()
                            if not apply_url:
                                apply_url = f"https://devpost.com/hackathons/{hid}"

                            org = h.get("organization_name") or "Devpost"
                            prize = _clean_prize(h.get("prize_amount", ""))
                            date_str = h.get("submission_period_dates", "")
                            reg_close = _parse_date(date_str)

                            themes = [t.get("name", "") for t in (h.get("themes") or []) if t.get("name")]

                            location = h.get("displayed_location", {})
                            is_online = location.get("icon", "") == "globe"
                            mode = "ONLINE" if is_online else "OFFLINE"

                            records.append(RawHackathon(
                                source_id=f"devpost-{hid}",
                                title=title,
                                organizer_name=org,
                                apply_url=apply_url,
                                registration_close=reg_close,
                                prize_pool=prize,
                                prize_currency="USD",
                                theme_tags=themes,
                                mode=mode,
                                scope="GLOBAL",
                            ))
                        except Exception:
                            continue

                    meta = data.get("meta", {})
                    total = meta.get("total_count", 0)
                    per_page = meta.get("per_page", 9)
                    if per_page > 0 and page * per_page >= total:
                        break
                    page += 1

                print(f"[{self.SOURCE}] API fetched {len(records)} records")

        except Exception as e:
            error = str(e)
            print(f"[{self.SOURCE}] Fatal error: {e}")

        status = "SUCCESS" if records else ("PARTIAL" if error else "FAILED")
        return ConnectorResult(source=self.SOURCE, records=records, status=status, error=error)
