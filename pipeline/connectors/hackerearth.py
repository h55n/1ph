"""
hackerearth.py — HackerEarth connector.
Method: Playwright (v2 API deprecated, v3 requires auth, page is JS-rendered).
Scrapes https://www.hackerearth.com/challenges/hackathon/
"""
import random

from .base import BaseConnector, ConnectorResult, RawHackathon

LIST_URL = "https://www.hackerearth.com/challenges/hackathon/"


class HackerEarthConnector(BaseConnector):
    SOURCE = "HACKEREARTH"
    SCOPE = "GLOBAL"

    def _parse_prize(self, text: str):
        if not text:
            return None
        import re
        text = text.replace(",", "").replace("$", "").replace("₹", "").strip()
        nums = re.findall(r"\d+(?:\.\d+)?", text)
        if nums:
            try:
                return float(nums[0])
            except ValueError:
                pass
        return None

    def fetch(self) -> ConnectorResult:
        from playwright.sync_api import sync_playwright

        records = []
        error = None

        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                ctx = browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                    ),
                    viewport={"width": 1366, "height": 768},
                )
                page = ctx.new_page()

                try:
                    print(f"[{self.SOURCE}] Navigating to {LIST_URL}...")
                    page.goto(LIST_URL, timeout=60000, wait_until="domcontentloaded")
                    page.wait_for_timeout(6000)

                    # Scroll to trigger lazy loading
                    for _ in range(3):
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        page.wait_for_timeout(random.randint(1500, 2000))

                    # Try common HackerEarth challenge card selectors
                    cards = page.query_selector_all(
                        ".challenge-card, .hackathon-card, "
                        "[class*='challenge-card'], [class*='hackathon-card'], "
                        ".card-content, article.challenge"
                    )
                    print(f"[{self.SOURCE}] Found {len(cards)} cards via primary selectors")

                    if not cards:
                        # Fallback: grab all hackathon links
                        links = page.query_selector_all("a[href*='/challenges/'][href*='/hackathon']")
                        seen = set()
                        for link in links:
                            try:
                                href = link.get_attribute("href") or ""
                                if not href or href in seen:
                                    continue
                                seen.add(href)
                                apply_url = href if href.startswith("http") else f"https://www.hackerearth.com{href}"
                                title_el = link.query_selector("h2, h3, .title, [class*='title']")
                                title = title_el.inner_text().strip() if title_el else link.inner_text().strip()
                                if not title or len(title) < 3:
                                    continue
                                records.append(RawHackathon(
                                    source_id=href.rstrip("/").split("/")[-1] or href,
                                    title=title,
                                    organizer_name="HackerEarth",
                                    apply_url=apply_url,
                                    registration_close="2099-12-31",
                                    mode="ONLINE",
                                    scope="GLOBAL",
                                ))
                            except Exception:
                                continue
                    else:
                        for card in cards:
                            try:
                                title_el = card.query_selector("h2, h3, .title, [class*='title'], .challenge-name")
                                link_el = card.query_selector("a[href]")
                                if not title_el or not link_el:
                                    continue

                                title = title_el.inner_text().strip()
                                href = link_el.get_attribute("href") or ""
                                apply_url = href if href.startswith("http") else f"https://www.hackerearth.com{href}"

                                prize_el = card.query_selector("[class*='prize'], [class*='reward'], .prize")
                                prize_text = prize_el.inner_text().strip() if prize_el else ""
                                prize = self._parse_prize(prize_text)

                                deadline_el = card.query_selector("[class*='deadline'], [class*='date'], time, .time-remaining")
                                deadline_text = deadline_el.inner_text().strip() if deadline_el else ""

                                org_el = card.query_selector("[class*='company'], [class*='org'], [class*='host']")
                                org = org_el.inner_text().strip() if org_el else "HackerEarth"

                                tags_els = card.query_selector_all("[class*='tag'], [class*='skill']")
                                tags = [t.inner_text().strip() for t in tags_els[:5] if t.inner_text().strip()]

                                records.append(RawHackathon(
                                    source_id=href.rstrip("/").split("/")[-1] or apply_url,
                                    title=title,
                                    organizer_name=org,
                                    apply_url=apply_url,
                                    registration_close="2099-12-31",
                                    prize_pool=prize,
                                    theme_tags=tags,
                                    mode="ONLINE",
                                    scope="GLOBAL",
                                ))
                            except Exception:
                                continue

                except Exception as e:
                    print(f"[{self.SOURCE}] Error: {e}")
                    error = str(e)
                finally:
                    browser.close()

        except Exception as e:
            error = str(e)

        status = "SUCCESS" if records else ("PARTIAL" if error else "FAILED")
        return ConnectorResult(source=self.SOURCE, records=records, status=status, error=error)
