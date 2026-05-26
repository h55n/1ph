"""
hackerrank.py — HackerRank connector.
Method: ZeroCrawl (browser mode for JS SPA).
Scrapes active programming contests & hackathons.
"""
import re
from bs4 import BeautifulSoup

from .base import BaseConnector, ConnectorResult, RawHackathon

LIST_URL = "https://www.hackerrank.com/contests"

# Blocklist — exclude internal "practice" or "interview prep" style content
BLOCKLIST = {"tutorial", "practice", "interview", "warmup", "week of code"}


def _is_blocked(title: str) -> bool:
    tl = title.lower()
    return any(b in tl for b in BLOCKLIST)


def _parse_html(html: str, records: list) -> int:
    """Parse contest cards from HackerRank HTML. Returns card count."""
    soup = BeautifulSoup(html, "html.parser")
    count = 0

    # Try card selectors
    cards = (
        soup.select(".contest-card") or
        soup.select("[class*='contest-card']") or
        soup.select("[class*='ContestCard']") or
        soup.select(".hackathon-item") or
        soup.select("[class*='hackathon-item']")
    )

    if cards:
        for card in cards:
            try:
                title_el = card.select_one("h2, h3, h4, [class*='title'], [class*='name'], [class*='contest-name'], [class*='hackathon-name']")
                link_el = card.select_one("a[href]")
                if not title_el or not link_el:
                    continue

                title = title_el.get_text(strip=True)
                if not title or _is_blocked(title):
                    continue

                href = link_el.get("href", "")
                apply_url = href if href.startswith("http") else f"https://www.hackerrank.com{href}"
                slug = href.rstrip("/").split("/")[-1]

                desc_el = card.select_one("p, [class*='desc'], [class*='description'], [class*='summary']")
                description = desc_el.get_text(strip=True)[:500] if desc_el else None

                org_el = card.select_one("[class*='company'], [class*='org'], [class*='host'], [class*='sponsor']")
                org = org_el.get_text(strip=True) if org_el else "HackerRank"

                prize_el = card.select_one("[class*='prize'], [class*='reward'], [class*='amount']")
                prize_text = prize_el.get_text(strip=True) if prize_el else ""
                nums = re.findall(r"[\d,]+", prize_text.replace(",", ""))
                prize = float(nums[0]) if nums else None

                records.append(RawHackathon(
                    source_id=f"hr-{slug}",
                    title=title,
                    organizer_name=org,
                    apply_url=apply_url,
                    registration_close="2099-12-31",
                    description=description,
                    prize_pool=prize,
                    mode="ONLINE",
                    scope="GLOBAL",
                ))
                count += 1
            except Exception:
                continue
    else:
        # Fallback: all contest links
        links = soup.select("a[href*='/contests/']")
        seen: set = set()
        for link in links:
            try:
                href = link.get("href", "")
                if not href or href == "/contests" or "?status" in href:
                    continue
                if href in seen:
                    continue
                seen.add(href)
                apply_url = href if href.startswith("http") else f"https://www.hackerrank.com{href}"
                title_el = link.select_one("h2, h3, h4, [class*='title'], [class*='name']")
                title = title_el.get_text(strip=True) if title_el else link.get_text(strip=True)
                if not title or len(title) < 4 or _is_blocked(title):
                    continue
                slug = href.rstrip("/").split("/")[-1]
                records.append(RawHackathon(
                    source_id=f"hr-{slug}",
                    title=title,
                    organizer_name="HackerRank",
                    apply_url=apply_url,
                    registration_close="2099-12-31",
                    mode="ONLINE",
                    scope="GLOBAL",
                ))
                count += 1
            except Exception:
                continue

    return count


class HackerRankConnector(BaseConnector):
    SOURCE = "HACKERRANK"
    SCOPE = "GLOBAL"

    def fetch(self) -> ConnectorResult:
        from ..zerocrawl_bridge import fetch_js_page

        records = []
        error = None

        try:
            print(f"[{self.SOURCE}] Fetching {LIST_URL} via ZeroCrawl browser mode...")
            html = fetch_js_page(LIST_URL, timeout=60)

            if not html:
                error = "ZeroCrawl returned empty response"
                print(f"[{self.SOURCE}] {error}")
            else:
                count = _parse_html(html, records)
                print(f"[{self.SOURCE}] Parsed {count} contests")

        except Exception as e:
            error = str(e)
            print(f"[{self.SOURCE}] Error: {e}")

        print(f"[{self.SOURCE}] Total: {len(records)} records")
        status = "SUCCESS" if records else ("PARTIAL" if error else "FAILED")
        return ConnectorResult(source=self.SOURCE, records=records, status=status, error=error)
