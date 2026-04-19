"""
unstop.py — Unstop connector. JS-rendered, Playwright.
Filters to hackathons only — excludes case studies, quizzes, debates.
India-focused.
"""
import random

from .base import BaseConnector, ConnectorResult, RawHackathon

LIST_URL = "https://unstop.com/hackathons"
BLOCKLIST = {"quiz", "case study", "debate", "trivia", "essay", "moot court", "management"}


def _is_blocked(title: str) -> bool:
    tl = title.lower()
    return any(b in tl for b in BLOCKLIST)


class UnstopConnector(BaseConnector):
    SOURCE = "UNSTOP"
    SCOPE = "INDIA"

    def _parse_prize(self, text: str):
        if not text:
            return None
        import re
        text = text.replace(",", "").replace("₹", "").replace("$", "")
        nums = re.findall(r"\d+(?:\.\d+)?", text)
        if nums:
            try:
                v = float(nums[0])
                # Convert lakhs shorthand: "5L" → 500000
                if "l" in text.lower() and v < 1000:
                    v *= 100000
                return v
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
                        "AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
                    ),
                    viewport={"width": 1366, "height": 768},
                )
                page = ctx.new_page()

                try:
                    page.goto(LIST_URL, timeout=30000, wait_until="networkidle")
                    page.wait_for_timeout(random.randint(3000, 5000))
                except Exception as e:
                    browser.close()
                    return ConnectorResult(source=self.SOURCE, records=[], status="FAILED", error=str(e))

                # Scroll to load more cards
                for _ in range(4):
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(random.randint(1500, 2500))

                cards = page.query_selector_all(".opportunity-card, [data-testid='opp-card'], .card.ng-star-inserted")

                for card in cards:
                    try:
                        title_el = card.query_selector("h3, .title, .opportunity-title, h2")
                        link_el = card.query_selector("a[href]")
                        if not title_el or not link_el:
                            continue

                        title = title_el.inner_text().strip()
                        if not title or _is_blocked(title):
                            continue

                        href = link_el.get_attribute("href") or ""
                        apply_url = href if href.startswith("http") else f"https://unstop.com{href}"

                        prize_el = card.query_selector(".prize, .reward, [class*='prize']")
                        prize_text = prize_el.inner_text().strip() if prize_el else ""
                        prize = self._parse_prize(prize_text)

                        org_el = card.query_selector(".org-name, .organiser, .host")
                        org = org_el.inner_text().strip() if org_el else "Unstop"

                        tags_els = card.query_selector_all(".tag, .category, [class*='tag']")
                        tags = [t.inner_text().strip() for t in tags_els[:5] if t.inner_text().strip()]

                        records.append(RawHackathon(
                            source_id=href.split("/")[-1] or apply_url,
                            title=title,
                            organizer_name=org,
                            apply_url=apply_url,
                            registration_close="2099-12-31",
                            prize_pool=prize,
                            prize_currency="INR",
                            theme_tags=tags,
                            mode="ONLINE",
                            scope="INDIA",
                        ))
                    except Exception:
                        continue

                browser.close()

        except Exception as e:
            error = str(e)

        status = "SUCCESS" if records else ("PARTIAL" if error else "FAILED")
        return ConnectorResult(source=self.SOURCE, records=records, status=status, error=error)
