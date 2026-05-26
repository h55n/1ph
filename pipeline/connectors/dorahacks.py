"""
dorahacks.py — DoraHacks connector.
Method: DoraHacks API endpoint as primary (much more reliable).
Fallback: ZeroCrawl browser mode (replaces raw Playwright).
"""
import re
from bs4 import BeautifulSoup

from .base import BaseConnector, ConnectorResult, RawHackathon

LIST_URL = "https://dorahacks.io/hackathon"
API_URL = "https://dorahacks.io/api/hackathon/?limit=50&offset=0&is_active=true&ordering=-created"


def _parse_prize(text: str):
    if not text:
        return None
    text = text.replace(",", "").replace("$", "").replace("USD", "").strip()
    nums = re.findall(r"\d+(?:\.\d+)?", text)
    if nums:
        try:
            return float(nums[0])
        except ValueError:
            pass
    return None


class DoraHacksConnector(BaseConnector):
    SOURCE = "DORAHACKS"
    SCOPE = "GLOBAL"

    def _try_api(self) -> list:
        """Try DoraHacks REST API first — much more reliable than scraping."""
        try:
            import httpx
            with httpx.Client(timeout=20, follow_redirects=True) as client:
                r = client.get(
                    API_URL,
                    headers={
                        "User-Agent": "Mozilla/5.0 (compatible; 1ph-bot/1.0)",
                        "Accept": "application/json",
                        "Referer": "https://dorahacks.io/hackathon",
                    }
                )
                if r.status_code == 200:
                    data = r.json()
                    items = data.get("results") or data.get("data") or []
                    records = []
                    for item in items:
                        try:
                            title = item.get("title") or item.get("name") or ""
                            if not title:
                                continue
                            slug_or_id = item.get("slug") or item.get("id") or ""
                            apply_url = f"https://dorahacks.io/hackathon/{slug_or_id}"
                            prize = item.get("prize_pool") or item.get("total_prize")
                            description = item.get("description") or item.get("intro") or None
                            records.append(RawHackathon(
                                source_id=f"dh-{slug_or_id}",
                                title=title,
                                organizer_name=item.get("organizer_name") or "DoraHacks",
                                apply_url=apply_url,
                                registration_close=str(item.get("end_time"))[:10] if item.get("end_time") else None,
                                prize_pool=float(prize) if prize else None,
                                prize_currency="USD",
                                description=str(description)[:500] if description else None,
                                mode="ONLINE",
                                scope="GLOBAL",
                            ))
                        except Exception:
                            continue
                    if records:
                        print(f"[{self.SOURCE}] API returned {len(records)} records")
                        return records
        except Exception as e:
            print(f"[{self.SOURCE}] API attempt failed: {e}")
        return []

    def _scrape_fallback(self) -> list:
        """ZeroCrawl browser fallback when API is unavailable."""
        from ..zerocrawl_bridge import fetch_js_page
        records = []

        try:
            print(f"[{self.SOURCE}] Fallback: ZeroCrawl browser mode for {LIST_URL}...")
            html = fetch_js_page(LIST_URL, timeout=90)
            if not html:
                return records

            soup = BeautifulSoup(html, "html.parser")

            # Try DoraHacks card selectors
            cards = (
                soup.select(".hackathon-card") or
                soup.select("[class*='hackathon-card']") or
                soup.select("[class*='HackathonCard']") or
                soup.select("[class*='buidl-card']") or
                soup.select("[class*='CardWrapper']") or
                soup.select("article[class*='hackathon']") or
                soup.select("div[class*='hackathon-item']")
            )

            if cards:
                for card in cards:
                    try:
                        title_el = card.select_one("h2, h3, [class*='title'], [class*='name']")
                        link_el = card.select_one("a[href]")
                        if not title_el or not link_el:
                            continue

                        title = title_el.get_text(strip=True)
                        href = link_el.get("href", "")
                        apply_url = href if href.startswith("http") else f"https://dorahacks.io{href}"
                        slug = href.rstrip("/").split("/")[-1]

                        prize_el = card.select_one("[class*='prize'], [class*='reward']")
                        prize_text = prize_el.get_text(strip=True) if prize_el else ""
                        prize = _parse_prize(prize_text)

                        desc_el = card.select_one("p, [class*='desc'], [class*='description']")
                        description = desc_el.get_text(strip=True)[:500] if desc_el else None

                        org_el = card.select_one("[class*='org'], [class*='organizer'], [class*='host']")
                        org = org_el.get_text(strip=True) if org_el else "DoraHacks"

                        tags_els = card.select("[class*='tag'], [class*='track']")
                        tags = [t.get_text(strip=True) for t in tags_els[:5] if t.get_text(strip=True)]

                        records.append(RawHackathon(
                            source_id=f"dh-{slug}",
                            title=title,
                            organizer_name=org,
                            apply_url=apply_url,
                            registration_close=None,
                            prize_pool=prize,
                            prize_currency="USD",
                            description=description,
                            theme_tags=tags,
                            mode="ONLINE",
                            scope="GLOBAL",
                        ))
                    except Exception:
                        continue
            else:
                # Last resort: extract links
                links = soup.select("a[href*='/hackathon/']")
                seen: set = set()
                for link in links:
                    try:
                        href = link.get("href", "")
                        if not href or href in seen or href == "/hackathon":
                            continue
                        seen.add(href)
                        apply_url = href if href.startswith("http") else f"https://dorahacks.io{href}"
                        title_el = link.select_one("h2, h3, [class*='title'], [class*='name']")
                        title = title_el.get_text(strip=True) if title_el else ""
                        if not title or len(title) < 3:
                            title = href.rstrip("/").split("/")[-1].replace("-", " ").title()
                        if not title:
                            continue
                        slug = href.rstrip("/").split("/")[-1]
                        records.append(RawHackathon(
                            source_id=f"dh-{slug}",
                            title=title,
                            organizer_name="DoraHacks",
                            apply_url=apply_url,
                            registration_close=None,
                            mode="ONLINE",
                            scope="GLOBAL",
                        ))
                    except Exception:
                        continue

            print(f"[{self.SOURCE}] Fallback collected {len(records)} records")
        except Exception as e:
            print(f"[{self.SOURCE}] Fallback error: {e}")

        return records

    def fetch(self) -> ConnectorResult:
        # Try API first
        api_records = self._try_api()
        if api_records:
            return ConnectorResult(source=self.SOURCE, records=api_records, status="SUCCESS", error=None)

        # Fallback: ZeroCrawl browser scraper
        records = self._scrape_fallback()
        status = "SUCCESS" if records else "FAILED"
        error = None if records else "Both API and browser fallback returned no records"
        return ConnectorResult(source=self.SOURCE, records=records, status=status, error=error)
