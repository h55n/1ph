"""
hackerearth.py — HackerEarth connector.
Method: httpx JSON API (primary) + Playwright (fallback).
HackerEarth has a public challenges API used by their mobile apps.
Scrapes https://www.hackerearth.com/challenges/hackathon/
"""
import random
import re

from .base import BaseConnector, ConnectorResult, RawHackathon

LIST_URL = "https://www.hackerearth.com/challenges/hackathon/"
# HackerEarth has an internal API endpoint used by their SPA
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

    def fetch(self) -> ConnectorResult:
        from playwright.sync_api import sync_playwright

        # Try API first
        api_records = self._try_api()
        if api_records:
            return ConnectorResult(source=self.SOURCE, records=api_records, status="SUCCESS", error=None)

        # Fallback: Playwright
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
                    print(f"[{self.SOURCE}] Playwright: Navigating to {LIST_URL}...")
                    page.goto(LIST_URL, timeout=60000, wait_until="domcontentloaded")
                    page.wait_for_timeout(6000)

                    # Scroll to trigger lazy loading
                    for _ in range(3):
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        page.wait_for_timeout(random.randint(1500, 2000))

                    SELECTORS = [
                        ".challenge-card",
                        ".hackathon-card",
                        "[class*='challenge-card']",
                        "[class*='hackathon-card']",
                        ".card-content",
                        "article.challenge",
                        "div[class*='challenge-list'] > div",
                        "li[class*='challenge']",
                    ]
                    cards = []
                    for sel in SELECTORS:
                        cards = page.query_selector_all(sel)
                        if cards:
                            print(f"[{self.SOURCE}] Found {len(cards)} cards with: {sel}")
                            break

                    if not cards:
                        # Fallback: grab all hackathon links
                        links = page.query_selector_all("a[href*='/challenges/'][href*='/hackathon']")
                        seen: set = set()
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
                    else:
                        for card in cards:
                            try:
                                title_el = card.query_selector(
                                    "h2, h3, .title, [class*='title'], .challenge-name, [class*='challenge-name']"
                                )
                                link_el = card.query_selector("a[href]")
                                if not title_el or not link_el:
                                    continue

                                title = title_el.inner_text().strip()
                                href = link_el.get_attribute("href") or ""
                                apply_url = href if href.startswith("http") else f"https://www.hackerearth.com{href}"
                                slug = href.rstrip("/").split("/")[-1]

                                prize_el = card.query_selector("[class*='prize'], [class*='reward'], .prize")
                                prize_text = prize_el.inner_text().strip() if prize_el else ""
                                prize = _parse_prize(prize_text)

                                desc_el = card.query_selector("p, [class*='desc'], [class*='description']")
                                description = desc_el.inner_text().strip()[:500] if desc_el else None

                                org_el = card.query_selector("[class*='company'], [class*='org'], [class*='host']")
                                org = org_el.inner_text().strip() if org_el else "HackerEarth"

                                tags_els = card.query_selector_all("[class*='tag'], [class*='skill']")
                                tags = [t.inner_text().strip() for t in tags_els[:5] if t.inner_text().strip()]

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
