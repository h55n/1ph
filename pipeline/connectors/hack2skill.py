"""
hack2skill.py — Hack2Skill connector. India's largest hackathon aggregator.
Method: ZeroCrawl (browser mode for React SPA).
Primary: https://hack2skill.com/hackathons
"""
import re
from bs4 import BeautifulSoup

from .base import BaseConnector, ConnectorResult, RawHackathon

LIST_URL = "https://hack2skill.com/hackathons"


def _parse_prize(text: str):
    if not text:
        return None
    text = text.replace(",", "").replace("₹", "").replace("$", "").strip()
    nums = re.findall(r"\d+(?:\.\d+)?", text)
    if nums:
        try:
            v = float(nums[0])
            if any(x in text.lower() for x in ["lakh", " l", "lac"]):
                if v < 10000:
                    v *= 100_000
            return v
        except ValueError:
            pass
    return None


def _parse_html(html: str, records: list) -> int:
    """Parse Hack2Skill hackathon cards from HTML. Returns card count."""
    soup = BeautifulSoup(html, "html.parser")
    count = 0

    # Try many card selector patterns for Hack2Skill's React SPA
    cards = (
        soup.select(".hackathon-card") or
        soup.select("[class*='hackathon-card']") or
        soup.select("[class*='HackathonCard']") or
        soup.select("[class*='eventCard']") or
        soup.select(".event-card") or
        soup.select("[class*='event-card']") or
        soup.select("[class*='CardWrapper']") or
        soup.select("[class*='competition-card']")
    )

    if cards:
        for card in cards:
            try:
                title_el = card.select_one("h2, h3, h4, [class*='title'], [class*='name'], [class*='heading']")
                link_el = card.select_one("a[href]")
                if not title_el or not link_el:
                    continue

                title = title_el.get_text(strip=True)
                if not title or len(title) < 3:
                    continue

                href = link_el.get("href", "")
                apply_url = href if href.startswith("http") else f"https://hack2skill.com{href}"

                prize_el = card.select_one("[class*='prize'], [class*='reward'], [class*='amount'], [class*='winning'], [class*='cash'], [class*='fund']")
                prize_text = prize_el.get_text(strip=True) if prize_el else ""
                prize = _parse_prize(prize_text)

                desc_el = card.select_one("p, [class*='desc'], [class*='description'], [class*='summary']")
                description = desc_el.get_text(strip=True)[:500] if desc_el else None

                org_el = card.select_one("[class*='org'], [class*='company'], [class*='host'], [class*='organizer'], [class*='institute'], [class*='college']")
                org = org_el.get_text(strip=True) if org_el else "Hack2Skill"

                tags_els = card.select("[class*='tag'], [class*='category'], [class*='track'], [class*='theme']")
                tags = [t.get_text(strip=True) for t in tags_els[:5] if t.get_text(strip=True)]

                records.append(RawHackathon(
                    source_id=f"h2s-{apply_url}",
                    title=title,
                    organizer_name=org,
                    apply_url=apply_url,
                    registration_close="2099-12-31",
                    description=description,
                    prize_pool=prize,
                    prize_currency="INR",
                    theme_tags=tags,
                    mode="ONLINE",
                    scope="INDIA",
                ))
                count += 1
            except Exception:
                continue
    else:
        # Fallback: grab all hackathon detail links
        links = soup.select("a[href*='/hackathon']")
        seen: set = set()
        for link in links:
            try:
                href = link.get("href", "")
                if not href or href in seen or href == "/hackathons":
                    continue
                seen.add(href)
                apply_url = href if href.startswith("http") else f"https://hack2skill.com{href}"
                title_el = link.select_one("h2, h3, h4, [class*='title'], [class*='name']")
                title = title_el.get_text(strip=True) if title_el else link.get_text(strip=True)
                title = title.strip()
                if not title or len(title) < 3:
                    title = href.rstrip("/").split("/")[-1].replace("-", " ").title()
                if not title:
                    continue
                records.append(RawHackathon(
                    source_id=f"h2s-{apply_url}",
                    title=title,
                    organizer_name="Hack2Skill",
                    apply_url=apply_url,
                    registration_close="2099-12-31",
                    mode="ONLINE",
                    scope="INDIA",
                    prize_currency="INR",
                ))
                count += 1
            except Exception:
                continue

    return count


class Hack2SkillConnector(BaseConnector):
    SOURCE = "HACK2SKILL"
    SCOPE = "INDIA"

    def fetch(self) -> ConnectorResult:
        from ..zerocrawl_bridge import fetch_js_page

        records = []
        error = None

        try:
            print(f"[{self.SOURCE}] Fetching {LIST_URL} via ZeroCrawl browser mode...")
            html = fetch_js_page(LIST_URL, timeout=90)

            if not html:
                error = "ZeroCrawl returned empty response"
                print(f"[{self.SOURCE}] {error}")
            else:
                count = _parse_html(html, records)
                print(f"[{self.SOURCE}] Parsed {count} hackathons")

        except Exception as e:
            error = str(e)
            print(f"[{self.SOURCE}] Error: {e}")

        print(f"[{self.SOURCE}] Total: {len(records)} records")
        status = "SUCCESS" if records else ("PARTIAL" if error else "FAILED")
        return ConnectorResult(source=self.SOURCE, records=records, status=status, error=error)
