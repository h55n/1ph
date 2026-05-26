"""
hackerearth.py — HackerEarth connector.
Method: httpx JSON API (primary) + ZeroCrawl browser fallback.
HackerEarth has a public challenges API used by their mobile apps.
"""
import re
from bs4 import BeautifulSoup

from .base import BaseConnector, ConnectorResult, RawHackathon

LIST_URL = "https://www.hackerearth.com/challenges/hackathon/"
API_URL = "https://www.hackerearth.com/challenges/json/challenges/?challenge_type=hackathon&status=ongoing&limit=50"


def _parse_prize(text: str):
    if not text:
        return None
    text = text.replace(",", "").replace("$", "").replace("₹", "").strip()
    nums = re.findall(r"\d+(?:\.\d+)?", text)
    if nums:
        try:
            return float(nums[0])
        except ValueError:
            pass
    return None


class HackerEarthConnector(BaseConnector):
    SOURCE = "HACKEREARTH"
    SCOPE = "GLOBAL"

    def _try_api(self) -> list:
        """Try HackerEarth JSON API."""
        try:
            import httpx
            with httpx.Client(timeout=20, follow_redirects=True) as client:
                r = client.get(
                    API_URL,
                    headers={
                        "User-Agent": "Mozilla/5.0 (compatible; 1ph-bot/1.0)",
                        "Accept": "application/json",
                        "Referer": "https://www.hackerearth.com/challenges/hackathon/",
                        "X-Requested-With": "XMLHttpRequest",
                    }
                )
                if r.status_code == 200:
                    data = r.json()
                    challenges = data.get("response", {}).get("challenges") or data.get("challenges") or []
                    records = []
                    for ch in challenges:
                        try:
                            title = ch.get("title") or ch.get("name") or ""
                            if not title:
                                continue
                            slug = ch.get("slug") or ch.get("url_name") or ch.get("id")
                            apply_url = ch.get("url") or f"https://www.hackerearth.com/challenges/hackathon/{slug}/"
                            if not apply_url.startswith("http"):
                                apply_url = f"https://www.hackerearth.com{apply_url}"
                            description = ch.get("description") or ch.get("short_description") or None
                            prize = ch.get("prize_amount") or None
                            org = ch.get("company") or ch.get("organization") or "HackerEarth"
                            records.append(RawHackathon(
                                source_id=f"he-{slug}",
                                title=title,
                                organizer_name=org,
                                apply_url=apply_url,
                                registration_close=str(ch.get("end_tz_date"))[:10] if ch.get("end_tz_date") else None,
                                description=str(description)[:500] if description else None,
                                prize_pool=float(prize) if prize else None,
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

            # Try card selectors
            cards = (
                soup.select(".challenge-card") or
                soup.select(".hackathon-card") or
                soup.select("[class*='challenge-card']") or
                soup.select("[class*='hackathon-card']") or
                soup.select(".card-content")
            )

            if cards:
                for card in cards:
                    try:
                        title_el = card.select_one(
                            "h2, h3, .title, [class*='title'], .challenge-name, [class*='challenge-name']"
                        )
                        link_el = card.select_one("a[href]")
                        if not title_el or not link_el:
                            continue

                        title = title_el.get_text(strip=True)
                        href = link_el.get("href", "")
                        apply_url = href if href.startswith("http") else f"https://www.hackerearth.com{href}"
                        slug = href.rstrip("/").split("/")[-1]

                        prize_el = card.select_one("[class*='prize'], [class*='reward'], .prize")
                        prize_text = prize_el.get_text(strip=True) if prize_el else ""
                        prize = _parse_prize(prize_text)

                        desc_el = card.select_one("p, [class*='desc'], [class*='description']")
                        description = desc_el.get_text(strip=True)[:500] if desc_el else None

                        org_el = card.select_one("[class*='company'], [class*='org'], [class*='host']")
                        org = org_el.get_text(strip=True) if org_el else "HackerEarth"

                        tags_els = card.select("[class*='tag'], [class*='skill']")
                        tags = [t.get_text(strip=True) for t in tags_els[:5] if t.get_text(strip=True)]

                        records.append(RawHackathon(
                            source_id=f"he-{slug}",
                            title=title,
                            organizer_name=org,
                            apply_url=apply_url,
                            registration_close=None,
                            description=description,
                            prize_pool=prize,
                            theme_tags=tags,
                            mode="ONLINE",
                            scope="GLOBAL",
                        ))
                    except Exception:
                        continue
            else:
                # Fallback: all hackathon links
                links = soup.select("a[href*='/challenges/'][href*='/hackathon']")
                seen: set = set()
                for link in links:
                    try:
                        href = link.get("href", "")
                        if not href or href in seen:
                            continue
                        seen.add(href)
                        apply_url = href if href.startswith("http") else f"https://www.hackerearth.com{href}"
                        title_el = link.select_one("h2, h3, .title, [class*='title']")
                        title = title_el.get_text(strip=True) if title_el else link.get_text(strip=True)
                        if not title or len(title) < 3:
                            continue
                        slug = href.rstrip("/").split("/")[-1]
                        records.append(RawHackathon(
                            source_id=f"he-{slug}",
                            title=title,
                            organizer_name="HackerEarth",
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
