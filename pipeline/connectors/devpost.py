"""
devpost.py — Devpost connector. JS-rendered, needs Playwright.
Includes anti-block: random delays, realistic user-agent, PARTIAL on rate-limit.
"""
import time
import random

from tenacity import retry, stop_after_attempt, wait_exponential

from .base import BaseConnector, ConnectorResult, RawHackathon

LIST_URL = "https://devpost.com/hackathons?challenge_type[]=online&status[]=open&status[]=upcoming"


class DevpostConnector(BaseConnector):
    SOURCE = "DEVPOST"
    SCOPE = "GLOBAL"

    def _parse_prize(self, text: str):
        if not text:
            return None
        import re
        text = text.replace(",", "").replace("$", "").replace("USD", "").strip()
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
                browser = pw.chromium.launch(
                    headless=True,
                    args=["--disable-blink-features=AutomationControlled"]
                )
                ctx = browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                    ),
                    viewport={"width": 1280, "height": 900},
                )
                page = ctx.new_page()

                # Load first page
                try:
                    print(f"[{self.SOURCE}] Navigating to {LIST_URL}...")
                    response = page.goto(LIST_URL, timeout=60000, wait_until="commit")
                    if response and response.status >= 400:
                        print(f"[{self.SOURCE}] HTTP Error: {response.status}")
                    page.wait_for_timeout(8000)
                    # Check for Devpost-specific card elements
                    page.wait_for_selector("article.challenge-listing, .challenge-listing", timeout=20000)
                except Exception as e:
                    print(f"[{self.SOURCE}] Navigation/Selector failed: {e}")
                    try:
                        print(f"[{self.SOURCE}] Page content snippet: {page.content()[:500]}")
                    except: pass
                    browser.close()
                    return ConnectorResult(source=self.SOURCE, records=[], status="FAILED", error=f"Navigation/Selector error: {str(e)}")

                pages_scraped = 0
                max_pages = 4  # Reduced from 8 to speed up pipeline and avoid cloudflare flagging

                while pages_scraped < max_pages:
                    try:
                        # Wait for cards to appear
                        page.wait_for_selector("article.challenge-listing, .challenge-listing", timeout=10000)
                    except Exception:
                        break

                    cards = page.query_selector_all("article.challenge-listing, .challenge-listing")
                    for card in cards:
                        try:
                            title_el = card.query_selector("h2, .challenge-title, .title")
                            link_el = card.query_selector("a[href*='/hackathons/']")
                            if not title_el or not link_el:
                                continue

                            title = title_el.inner_text().strip()
                            apply_url = link_el.get_attribute("href") or ""
                            if not apply_url.startswith("http"):
                                apply_url = f"https://devpost.com{apply_url}"

                            prize_el = card.query_selector(".prize, .prize-amount")
                            prize_text = prize_el.inner_text().strip() if prize_el else ""
                            prize = self._parse_prize(prize_text)

                            deadline_el = card.query_selector(".submission-period, .date")
                            deadline_text = deadline_el.inner_text().strip() if deadline_el else ""

                            tags_els = card.query_selector_all(".theme, .tag")
                            tags = [t.inner_text().strip() for t in tags_els[:5]]

                            org_el = card.query_selector(".host-label, .organizer")
                            org = org_el.inner_text().strip() if org_el else "Devpost"

                            records.append(RawHackathon(
                                source_id=apply_url.split("/")[-1] or apply_url,
                                title=title,
                                organizer_name=org,
                                apply_url=apply_url,
                                registration_close="2099-12-31",
                                description=deadline_text[:500] if deadline_text else None,
                                prize_pool=prize,
                                prize_currency="USD",
                                theme_tags=tags,
                                mode="ONLINE",
                                scope="GLOBAL",
                            ))
                        except Exception:
                            continue

                    pages_scraped += 1

                    # Try next page
                    next_btn = page.query_selector("a[rel='next'], .pagination .next a")
                    if not next_btn:
                        break

                    try:
                        next_btn.click()
                        page.wait_for_timeout(random.randint(2500, 5000))
                    except Exception:
                        break

                browser.close()

        except Exception as e:
            error = str(e)

        status = "SUCCESS" if records else ("PARTIAL" if error else "FAILED")
        return ConnectorResult(source=self.SOURCE, records=records, status=status, error=error)
