"""
unstop.py — Unstop connector. JS-rendered Angular SPA.
Method: ZeroCrawl (browser mode with anti-detection).
India-focused. Filters to hackathons only.
"""
import re
from bs4 import BeautifulSoup

from .base import BaseConnector, ConnectorResult, RawHackathon

LIST_URL = "https://unstop.com/hackathons"
BLOCKLIST = {"quiz", "case study", "debate", "trivia", "essay", "moot court", "management", "contest"}


def _is_blocked(title: str) -> bool:
    tl = title.lower()
    return any(b in tl for b in BLOCKLIST)


def _parse_prize(text: str):
    if not text:
        return None
    text = text.replace(",", "").replace("₹", "").replace("$", "").replace("USD", "")
    nums = re.findall(r"\d+(?:\.\d+)?", text)
    if nums:
        try:
            v = float(nums[0])
            if "l" in text.lower() and v < 1000:
                v *= 100_000
            return v
        except ValueError:
            pass
    return None


def _parse_html(html: str, records: list) -> int:
    """Parse hackathon cards from Unstop HTML. Returns count of cards found."""
    soup = BeautifulSoup(html, "html.parser")
    count = 0

    # Try various card selectors
    cards = (
        soup.select("div[class*='opportunity']") or
        soup.select("div[class*='card-wrapper']") or
        soup.select("app-opportunity-card") or
        soup.select("div[class*='listing__card']") or
        soup.select("div[class*='single-opportunity']")
    )

    if cards:
        for card in cards:
            try:
                title_el = card.select_one("h3, h2, [class*='title'], [class*='name'], [class*='opportunity-name']")
                if not title_el:
                    continue
                title = title_el.get_text(strip=True)
                if not title or _is_blocked(title):
                    continue

                link_el = card.select_one("a[href]")
                if not link_el:
                    continue
                href = link_el.get("href", "")
                apply_url = href if href.startswith("http") else f"https://unstop.com{href}"
                slug = href.rstrip("/").split("/")[-1]

                prize_el = card.select_one("[class*='prize'], [class*='reward'], [class*='amount'], [class*='winning'], [class*='cash']")
                prize_text = prize_el.get_text(strip=True) if prize_el else ""
                prize = _parse_prize(prize_text)

                org_el = card.select_one("[class*='org'], [class*='company'], [class*='host'], [class*='organizer'], [class*='institute']")
                org = org_el.get_text(strip=True) if org_el else "Unstop"

                tags_els = card.select("[class*='tag'], [class*='category'], [class*='track']")
                tags = [t.get_text(strip=True) for t in tags_els[:5] if t.get_text(strip=True)]

                records.append(RawHackathon(
                    source_id=f"unstop-{slug}",
                    title=title,
                    organizer_name=org,
                    apply_url=apply_url,
                    registration_close=None,
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
        # Fallback: grab all hackathon links
        links = soup.select("a[href*='/hackathon'], a[href*='/o/']")
        seen: set = set()
        for link in links:
            try:
                href = link.get("href", "")
                if not href or href in seen:
                    continue
                if href in ["/hackathons", "https://unstop.com/hackathons"]:
                    continue
                seen.add(href)
                apply_url = href if href.startswith("http") else f"https://unstop.com{href}"
                raw_title = link.get("aria-label") or link.get_text(strip=True)
                title = raw_title.split('\n')[0].strip() if raw_title else ""
                if not title or len(title) < 4 or _is_blocked(title):
                    continue
                slug = href.rstrip("/").split("/")[-1]
                records.append(RawHackathon(
                    source_id=f"unstop-{slug}",
                    title=title,
                    organizer_name="Unstop",
                    apply_url=apply_url,
                    registration_close=None,
                    mode="ONLINE",
                    scope="INDIA",
                ))
                count += 1
            except Exception:
                continue

    return count


class UnstopConnector(BaseConnector):
    SOURCE = "UNSTOP"
    SCOPE = "INDIA"

    def fetch(self) -> ConnectorResult:
        from ..zerocrawl_bridge import fetch_js_page

        records = []
        error = None

        try:
            print(f"[{self.SOURCE}] Fetching {LIST_URL} via ZeroCrawl browser mode...")
            # Unstop is an Angular SPA — force browser mode
            html = fetch_js_page(
                LIST_URL,
                wait_for_selector="div[class*='opportunity'], app-opportunity-card",
                timeout=90,
            )

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
