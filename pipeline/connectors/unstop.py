"""
unstop.py — Unstop connector. JS-rendered Angular SPA, Playwright.
Filters to hackathons only — excludes case studies, quizzes, debates.
India-focused.
"""
import random
import re

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


class UnstopConnector(BaseConnector):
    SOURCE = "UNSTOP"
    SCOPE = "INDIA"

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
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                    ),
                    viewport={"width": 1366, "height": 768},
                )
                page = ctx.new_page()

                try:
                    print(f"[{self.SOURCE}] Navigating to {LIST_URL}...")
                    page.goto(LIST_URL, timeout=60000, wait_until="domcontentloaded")
                    page.wait_for_timeout(8000)

                    # Scroll to trigger Angular lazy loading
                    for _ in range(5):
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        page.wait_for_timeout(random.randint(1500, 2500))

                    # Unstop uses Angular — try multiple selector patterns
                    # Primary: opportunity cards
                    CARD_SELECTORS = [
                        "div[class*='opportunity']",
                        "div[class*='card-wrapper']",
                        "app-opportunity-card",
                        "div[class*='listing__card']",
                        "div[class*='single-opportunity']",
                    ]
                    cards = []
                    for sel in CARD_SELECTORS:
                        cards = page.query_selector_all(sel)
                        if cards:
                            print(f"[{self.SOURCE}] Found {len(cards)} cards with selector: {sel}")
                            break

                    if not cards:
                        print(f"[{self.SOURCE}] No cards found via primary; falling back to links")
                        # Fallback: all /o/ or /hackathon links
                        links = page.query_selector_all("a[href*='/hackathon'], a[href*='/o/']")
                        seen: set = set()
                        for link in links:
                            try:
                                href = link.get_attribute("href") or ""
                                if not href or href in seen:
                                    continue
                                # Skip navigation links
                                if href in ["/hackathons", "https://unstop.com/hackathons"]:
                                    continue
                                seen.add(href)
                                apply_url = href if href.startswith("http") else f"https://unstop.com{href}"
                                # Title from aria-label or inner text
                                raw_title = link.get_attribute("aria-label") or link.inner_text().strip()
                                title = raw_title.split('\n')[0].strip() if raw_title else ""
                                if not title or len(title) < 4 or _is_blocked(title):
                                    continue
                                slug = href.rstrip("/").split("/")[-1]
                                records.append(RawHackathon(
                                    source_id=f"unstop-{slug}",
                                    title=title,
                                    organizer_name="Unstop",
                                    apply_url=apply_url,
                                    registration_close="2099-12-31",
                                    mode="ONLINE",
                                    scope="INDIA",
                                ))
                            except Exception:
                                continue
                    else:
                        for card in cards:
                            try:
                                # Title
                                title_el = card.query_selector(
                                    "h3, h2, [class*='title'], [class*='name'], [class*='opportunity-name']"
                                )
                                if not title_el:
                                    continue
                                title = title_el.inner_text().strip()
                                if not title or _is_blocked(title):
                                    continue

                                # Link
                                link_el = card.query_selector("a[href]")
                                if not link_el:
                                    continue
                                href = link_el.get_attribute("href") or ""
                                apply_url = href if href.startswith("http") else f"https://unstop.com{href}"
                                slug = href.rstrip("/").split("/")[-1]

                                # Prize
                                prize_el = card.query_selector(
                                    "[class*='prize'], [class*='reward'], [class*='amount'], "
                                    "[class*='winning'], [class*='cash']"
                                )
                                prize_text = prize_el.inner_text().strip() if prize_el else ""
                                prize = _parse_prize(prize_text)

                                # Organizer
                                org_el = card.query_selector(
                                    "[class*='org'], [class*='company'], [class*='host'], "
                                    "[class*='organizer'], [class*='institute']"
                                )
                                org = org_el.inner_text().strip() if org_el else "Unstop"

                                # Tags
                                tags_els = card.query_selector_all("[class*='tag'], [class*='category'], [class*='track']")
                                tags = [t.inner_text().strip() for t in tags_els[:5] if t.inner_text().strip()]

                                records.append(RawHackathon(
                                    source_id=f"unstop-{slug}",
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

                    print(f"[{self.SOURCE}] Collected {len(records)} records")

                except Exception as e:
                    print(f"[{self.SOURCE}] Error: {e}")
                    error = str(e)
                finally:
                    browser.close()

        except Exception as e:
            error = str(e)

        status = "SUCCESS" if records else ("PARTIAL" if error else "FAILED")
        return ConnectorResult(source=self.SOURCE, records=records, status=status, error=error)
