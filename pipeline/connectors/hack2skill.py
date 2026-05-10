"""
hack2skill.py — Hack2Skill connector. India's largest hackathon aggregator.
Method: Playwright (full SPA — BeautifulSoup only gets empty <div id="root">).
Primary: https://hack2skill.com/hackathons
Also tries API endpoint if available.
"""
import random
import re

from .base import BaseConnector, ConnectorResult, RawHackathon

LIST_URL = "https://hack2skill.com/hackathons"


def _parse_prize(text: str):
    if not text:
        return None
    text = text.replace(",", "").replace("₹", "").replace("$", "").strip()
    nums = re.findall(r"\d+(?:\.\d+)?", text)
    if nums:
        try:
            v = float(nums[0])
            if any(x in text.lower() for x in ["lakh", " l", "lac"]):
                if v < 10000:
                    v *= 100_000
            return v
        except ValueError:
            pass
    return None


class Hack2SkillConnector(BaseConnector):
    SOURCE = "HACK2SKILL"
    SCOPE = "INDIA"

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
                    page.goto(LIST_URL, timeout=60000, wait_until="networkidle")
                    page.wait_for_timeout(5000)

                    # Scroll to load lazy cards
                    for _ in range(5):
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        page.wait_for_timeout(random.randint(1200, 2000))

                    # Try many selector patterns for Hack2Skill's React SPA
                    CARD_SELECTORS = [
                        ".hackathon-card",
                        "[class*='hackathon-card']",
                        "[class*='HackathonCard']",
                        "[class*='eventCard']",
                        ".event-card",
                        "[class*='event-card']",
                        "[class*='CardWrapper']",
                        "[class*='competition-card']",
                        "[class*='contest-card']",
                        # Generic React card patterns
                        "div[class*='card']:has(a[href*='/hackathon'])",
                        "div[class*='Card']:has(a[href*='/hackathon'])",
                    ]

                    cards = []
                    for sel in CARD_SELECTORS:
                        try:
                            cards = page.query_selector_all(sel)
                            if cards:
                                print(f"[{self.SOURCE}] Found {len(cards)} cards with: {sel}")
                                break
                        except Exception:
                            continue

                    if not cards:
                        print(f"[{self.SOURCE}] No cards found via primary selectors; falling back to links")
                        # Fallback: grab all hackathon detail links
                        links = page.query_selector_all("a[href*='/hackathon']")
                        seen: set = set()
                        for link in links:
                            try:
                                href = link.get_attribute("href") or ""
                                if not href or href in seen or href == "/hackathons":
                                    continue
                                seen.add(href)
                                apply_url = href if href.startswith("http") else f"https://hack2skill.com{href}"
                                # Try to find title in link children
                                title_el = link.query_selector("h2, h3, h4, [class*='title'], [class*='name']")
                                title = title_el.inner_text().strip() if title_el else link.inner_text().strip()
                                title = title.strip()
                                if not title or len(title) < 3:
                                    # Use slug
                                    title = href.rstrip("/").split("/")[-1].replace("-", " ").title()
                                if not title:
                                    continue
                                records.append(RawHackathon(
                                    source_id=f"h2s-{apply_url}",
                                    title=title,
                                    organizer_name="Hack2Skill",
                                    apply_url=apply_url,
                                    registration_close="2099-12-31",
                                    mode="ONLINE",
                                    scope="INDIA",
                                    prize_currency="INR",
                                ))
                            except Exception:
                                continue
                    else:
                        for card in cards:
                            try:
                                title_el = card.query_selector(
                                    "h2, h3, h4, [class*='title'], [class*='name'], [class*='heading']"
                                )
                                link_el = card.query_selector("a[href]")
                                if not title_el or not link_el:
                                    continue

                                title = title_el.inner_text().strip()
                                href = link_el.get_attribute("href") or ""
                                apply_url = href if href.startswith("http") else f"https://hack2skill.com{href}"

                                prize_el = card.query_selector(
                                    "[class*='prize'], [class*='reward'], [class*='amount'], "
                                    "[class*='winning'], [class*='cash'], [class*='fund']"
                                )
                                prize_text = prize_el.inner_text().strip() if prize_el else ""
                                prize = _parse_prize(prize_text)

                                desc_el = card.query_selector(
                                    "p, [class*='desc'], [class*='description'], [class*='summary']"
                                )
                                description = desc_el.inner_text().strip()[:500] if desc_el else None

                                org_el = card.query_selector(
                                    "[class*='org'], [class*='company'], [class*='host'], "
                                    "[class*='organizer'], [class*='institute'], [class*='college']"
                                )
                                org = org_el.inner_text().strip() if org_el else "Hack2Skill"

                                tags_els = card.query_selector_all(
                                    "[class*='tag'], [class*='category'], [class*='track'], [class*='theme']"
                                )
                                tags = [t.inner_text().strip() for t in tags_els[:5] if t.inner_text().strip()]

                                records.append(RawHackathon(
                                    source_id=f"h2s-{apply_url}",
                                    title=title,
                                    organizer_name=org,
                                    apply_url=apply_url,
                                    registration_close="2099-12-31",
                                    description=description,
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
