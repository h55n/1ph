"""
luma.py — lu.ma connector.
Scrapes lu.ma for hackathons using Playwright.
"""
from typing import List
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from .base import BaseConnector, ConnectorResult, RawHackathon


class LumaConnector(BaseConnector):
    SOURCE = "LUMA"
    SCOPE = "GLOBAL"

    def fetch(self) -> ConnectorResult:
        records: List[RawHackathon] = []
        error = None

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--disable-setuid-sandbox"
                    ]
                )
                context = browser.new_context(
                    viewport={"width": 1280, "height": 800},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                )
                page = context.new_page()

                # Popular tech cities for discovery
                cities = ["san-francisco", "bengaluru", "london", "new-york", "pune", "delhi", "mumbai", "hyderabad", "chennai", "singapore", "berlin", "toronto"]

                seen_slugs = set()
                for city in cities:
                    url = f"https://lu.ma/{city}"
                    print(f"[{self.SOURCE}] Scraping city: {city} ({url})")

                    try:
                        page.goto(url, timeout=30000, wait_until="domcontentloaded")
                        page.wait_for_timeout(2500)
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        page.wait_for_timeout(2500)
                    except PlaywrightTimeoutError:
                        print(f"[{self.SOURCE}] Timeout loading city: {city}")
                        continue

                    links = page.locator("a[href^='/']").all()
                    print(f"[{self.SOURCE}] Found {len(links)} raw links on city page.")

                    for link in links:
                        try:
                            href = link.get_attribute("href")
                            if not href or href == "/" or href.startswith("/explore") or href.startswith("/search") or href.startswith("/create") or href.startswith("/home") or href.startswith("/calendar"):
                                continue

                            slug = href.lstrip("/")
                            if len(slug) < 4 or " " in slug or slug in seen_slugs:
                                continue

                            try:
                                title = link.inner_text().strip().split('\n')[0]
                            except Exception:
                                continue

                            if not title or len(title) < 5 or ("hackathon" not in title.lower() and "hack" not in title.lower() and "build" not in title.lower() and "dev" not in title.lower()):
                                continue

                            seen_slugs.add(slug)
                            apply_url = f"https://lu.ma/{slug}"
                            text_content = link.inner_text()

                            mode = "OFFLINE" if "in person" in text_content.lower() or "offline" in text_content.lower() else "ONLINE"

                            records.append(RawHackathon(
                                source_id=f"luma-{slug}",
                                title=title,
                                organizer_name="Luma Host",
                                apply_url=apply_url,
                                registration_close="2099-12-31",
                                description=text_content.replace('\n', ' ')[:500],
                                prize_pool=None,
                                prize_currency="USD",
                                mode=mode,
                                scope="GLOBAL",
                                sponsors=["lu.ma"]
                            ))
                        except Exception:
                            continue

                browser.close()

        except Exception as e:
            error = str(e)
            print(f"[{self.SOURCE}] Pipeline error: {e}")

        # Deduplicate
        unique = {r.apply_url: r for r in records}.values()
        
        print(f"[{self.SOURCE}] Found {len(unique)} unique hackathons.")
        status = "SUCCESS" if unique else ("PARTIAL" if error else "FAILED")
        return ConnectorResult(source=self.SOURCE, records=list(unique), status=status, error=error)
