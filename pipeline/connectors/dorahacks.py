"""
dorahacks.py - DoraHacks connector.
Uses DoraHacks API endpoint as primary, Playwright as fallback.
"""
import random
import re

from .base import BaseConnector, ConnectorResult, RawHackathon

LIST_URL = "https://dorahacks.io/hackathon"
API_URL = "https://dorahacks.io/api/hackathon/?limit=50&offset={offset}&is_active=true&ordering=-created"


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
        """Try DoraHacks REST API first - much more reliable than scraping."""
        try:
            import httpx
            with httpx.Client(timeout=20, follow_redirects=True) as client:
                records = []
                seen = set()
                for offset in range(0, 200, 50):
                    r = client.get(
                        API_URL.format(offset=offset),
                        headers={
                            "User-Agent": "Mozilla/5.0 (compatible; 1ph-bot/1.0)",
                            "Accept": "application/json",
                            "Referer": "https://dorahacks.io/hackathon",
                        }
                    )
                    if r.status_code != 200:
                        break
                    data = r.json()
                    items = data.get("results") or data.get("data") or []
                    if not items:
                        break
                    for item in items:
                        try:
                            title = item.get("title") or item.get("name") or ""
                            if not title:
                                continue
                            slug_or_id = item.get("slug") or item.get("id") or ""
                            if slug_or_id in seen:
                                continue
                            seen.add(slug_or_id)
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

    def fetch(self) -> ConnectorResult:
        from playwright.sync_api import sync_playwright

        api_records = self._try_api()
        if api_records:
            return ConnectorResult(source=self.SOURCE, records=api_records, status="SUCCESS", error=None)

        records = []
        error = None

        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                ctx = browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                    ),
                    viewport={"width": 1280, "height": 900},
                )
                page = ctx.new_page()

                try:
                    print(f"[{self.SOURCE}] Playwright: Navigating to {LIST_URL}...")
                    page.goto(LIST_URL, timeout=60000, wait_until="domcontentloaded")
                    page.wait_for_timeout(6000)

                    for _ in range(4):
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        page.wait_for_timeout(random.randint(1500, 2500))

                    SELECTORS = [
                        ".hackathon-card",
                        "[class*='hackathon-card']",
                        "[class*='HackathonCard']",
                        "[class*='buidl-card']",
                        "[class*='CardWrapper']",
                        "article[class*='hackathon']",
                        "div[class*='hackathon-item']",
                    ]
                    cards = []
                    for sel in SELECTORS:
                        cards = page.query_selector_all(sel)
                        if cards:
                            print(f"[{self.SOURCE}] Found {len(cards)} cards with: {sel}")
                            break

                    if not cards:
                        print(f"[{self.SOURCE}] Fallback to link scraping")
                        links = page.query_selector_all("a[href*='/hackathon/']")
                        seen: set = set()
                        for link in links:
                            try:
                                href = link.get_attribute("href") or ""
                                if not href or href in seen or href == "/hackathon":
                                    continue
                                seen.add(href)
                                apply_url = href if href.startswith("http") else f"https://dorahacks.io{href}"
                                title_el = link.query_selector("h2, h3, [class*='title'], [class*='name']")
                                title = title_el.inner_text().strip() if title_el else ""
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
                    else:
                        for card in cards:
                            try:
                                title_el = card.query_selector("h2, h3, [class*='title'], [class*='name']")
                                is_a_tag = card.evaluate("node => node.tagName.toLowerCase() === 'a'")
                                link_el = card if is_a_tag else card.query_selector("a[href]")
                                if not title_el or not link_el:
                                    continue

                                title = title_el.inner_text().strip()
                                href = link_el.get_attribute("href") or ""
                                apply_url = href if href.startswith("http") else f"https://dorahacks.io{href}"
                                slug = href.rstrip("/").split("/")[-1]

                                prize_el = card.query_selector("[class*='prize'], [class*='reward']")
                                prize_text = prize_el.inner_text().strip() if prize_el else ""
                                prize = _parse_prize(prize_text)

                                desc_el = card.query_selector("p, [class*='desc'], [class*='description']")
                                description = desc_el.inner_text().strip()[:500] if desc_el else None

                                org_el = card.query_selector("[class*='org'], [class*='organizer'], [class*='host']")
                                org = org_el.inner_text().strip() if org_el else "DoraHacks"

                                tags_els = card.query_selector_all("[class*='tag'], [class*='track']")
                                tags = [t.inner_text().strip() for t in tags_els[:5] if t.inner_text().strip()]

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

                    print(f"[{self.SOURCE}] Playwright collected {len(records)} records")

                except Exception as e:
                    print(f"[{self.SOURCE}] Error: {e}")
                    error = str(e)
                finally:
                    browser.close()

        except Exception as e:
            error = str(e)

        status = "SUCCESS" if records else ("PARTIAL" if error else "FAILED")
        return ConnectorResult(source=self.SOURCE, records=records, status=status, error=error)
