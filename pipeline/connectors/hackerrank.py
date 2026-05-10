"""
hackerrank.py — HackerRank connector.
Method: Playwright (JS-rendered SPA).
Scrapes https://www.hackerrank.com/contests — active programming contests & hackathons.
"""
import random

from .base import BaseConnector, ConnectorResult, RawHackathon

LIST_URL = "https://www.hackerrank.com/contests"

# Blocklist — exclude internal "practice" or "interview prep" style content
BLOCKLIST = {"tutorial", "practice", "interview", "warmup", "week of code"}


def _is_blocked(title: str) -> bool:
    tl = title.lower()
    return any(b in tl for b in BLOCKLIST)


class HackerRankConnector(BaseConnector):
    SOURCE = "HACKERRANK"
    SCOPE = "GLOBAL"

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
                    page.wait_for_timeout(5000)

                    # Scroll to trigger lazy loading
                    for _ in range(3):
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        page.wait_for_timeout(random.randint(1500, 2500))

                    # HackerRank contest cards
                    cards = page.query_selector_all(
                        ".contest-card, [class*='contest-card'], "
                        "[class*='ContestCard'], "
                        ".hackathon-item, [class*='hackathon-item'], "
                        "li[class*='contest'], div[class*='contest-list'] > div"
                    )
                    print(f"[{self.SOURCE}] Found {len(cards)} cards via primary selectors")

                    if not cards:
                        # Fallback: find all contest links
                        links = page.query_selector_all("a[href*='/contests/']")
                        seen: set = set()
                        for link in links:
                            try:
                                href = link.get_attribute("href") or ""
                                # Skip navigation/filter links
                                if not href or href == "/contests" or "?status" in href:
                                    continue
                                if href in seen:
                                    continue
                                seen.add(href)
                                apply_url = (
                                    href if href.startswith("http")
                                    else f"https://www.hackerrank.com{href}"
                                )
                                title_el = link.query_selector("h2, h3, h4, [class*='title'], [class*='name']")
                                title = title_el.inner_text().strip() if title_el else link.inner_text().strip()
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
                            except Exception:
                                continue
                    else:
                        for card in cards:
                            try:
                                title_el = card.query_selector(
                                    "h2, h3, h4, [class*='title'], [class*='name'], "
                                    "[class*='contest-name'], [class*='hackathon-name']"
                                )
                                link_el = card.query_selector("a[href]")
                                if not title_el or not link_el:
                                    continue

                                title = title_el.inner_text().strip()
                                if not title or _is_blocked(title):
                                    continue

                                href = link_el.get_attribute("href") or ""
                                apply_url = (
                                    href if href.startswith("http")
                                    else f"https://www.hackerrank.com{href}"
                                )
                                slug = href.rstrip("/").split("/")[-1]

                                desc_el = card.query_selector(
                                    "p, [class*='desc'], [class*='description'], [class*='summary']"
                                )
                                description = desc_el.inner_text().strip()[:500] if desc_el else None

                                org_el = card.query_selector(
                                    "[class*='company'], [class*='org'], [class*='host'], [class*='sponsor']"
                                )
                                org = org_el.inner_text().strip() if org_el else "HackerRank"

                                prize_el = card.query_selector(
                                    "[class*='prize'], [class*='reward'], [class*='amount']"
                                )
                                prize_text = prize_el.inner_text().strip() if prize_el else ""

                                import re
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
                            except Exception:
                                continue

                except Exception as e:
                    print(f"[{self.SOURCE}] Error: {e}")
                    error = str(e)
                finally:
                    browser.close()

        except Exception as e:
            error = str(e)

        print(f"[{self.SOURCE}] Total: {len(records)} records")
        status = "SUCCESS" if records else ("PARTIAL" if error else "FAILED")
        return ConnectorResult(source=self.SOURCE, records=records, status=status, error=error)
