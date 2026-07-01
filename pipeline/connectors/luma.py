"""
luma.py — lu.ma connector.
Scrapes lu.ma city pages using Playwright with broad keyword matching.
"""
from typing import List

from .base import BaseConnector, ConnectorResult, RawHackathon

# City pages for discovery
CITIES = [
    "san-francisco", "bengaluru", "london", "new-york", "pune",
    "delhi", "mumbai", "hyderabad", "chennai", "singapore", "berlin", "toronto"
]

# Very broad set — Luma hosts many tech events that are hackathon-adjacent
HACK_KEYWORDS = {
    "hackathon", "hack", "build", "buildathon", "buildweek", "codefest",
    "dev", "developer", "code", "coding", "sprint",
    "ai", "ml", "web3", "blockchain", "crypto", "defi", "nft",
    "startup", "founder", "fintech", "open source",
}


def _is_hackathon(title: str, description: str = "") -> bool:
    text = f"{title} {description}".lower()
    return any(kw in text for kw in HACK_KEYWORDS)


class LumaConnector(BaseConnector):
    SOURCE = "LUMA"
    SCOPE = "GLOBAL"

    def _try_playwright(self) -> list:
        """Playwright fallback: scrape city event pages."""
        from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

        records: List[RawHackathon] = []
        seen_slugs: set = set()

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
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                page = context.new_page()

                for city in CITIES:
                    url = f"https://lu.ma/{city}"
                    print(f"[{self.SOURCE}] Scraping city: {city} ({url})")
                    try:
                        page.goto(url, timeout=30000, wait_until="domcontentloaded")
                        page.wait_for_timeout(2500)
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        page.wait_for_timeout(2500)
                    except PlaywrightTimeoutError:
                        continue

                    links = page.locator("a[href^='/']").all()
                    print(f"[{self.SOURCE}] Found {len(links)} raw links on {city}")

                    for link in links:
                        try:
                            href = link.get_attribute("href")
                            if not href or href in ("/", "/explore", "/search", "/create", "/home", "/calendar"):
                                continue
                            if any(href.startswith(x) for x in ["/explore", "/search", "/create", "/home", "/calendar", "/login"]):
                                continue

                            slug = href.lstrip("/")
                            if len(slug) < 4 or " " in slug or slug in seen_slugs:
                                continue

                            try:
                                text_content = link.inner_text().strip()
                                title = text_content.split('\n')[0].strip()
                            except Exception:
                                continue

                            if not title or len(title) < 5:
                                continue

                            # Broader keyword matching for Luma events
                            if not _is_hackathon(title, text_content):
                                continue

                            seen_slugs.add(slug)
                            apply_url = f"https://lu.ma/{slug}"
                            mode = "OFFLINE" if any(x in text_content.lower() for x in ["in person", "offline", "venue"]) else "ONLINE"
                            scope = "INDIA" if any(c in city for c in ["bengaluru", "pune", "delhi", "mumbai", "hyderabad", "chennai"]) else "GLOBAL"

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
                                scope=scope,
                                sponsors=["lu.ma"]
                            ))
                        except Exception:
                            continue

                browser.close()
        except Exception as e:
            print(f"[{self.SOURCE}] Playwright error: {e}")

        return records

    def fetch(self) -> ConnectorResult:
        records = self._try_playwright()

        # Deduplicate
        unique = {r.apply_url: r for r in records}
        print(f"[{self.SOURCE}] Found {len(unique)} unique hackathons.")
        status = "SUCCESS" if unique else "FAILED"
        return ConnectorResult(source=self.SOURCE, records=list(unique.values()), status=status, error=None)
