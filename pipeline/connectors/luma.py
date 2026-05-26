"""
luma.py — lu.ma connector.
Method: ZeroCrawl (browser mode for JS SPA).
Scrapes lu.ma city pages for hackathon events.

Bug fixed: Previous version navigated through city pages but only read links
from the LAST page. Now correctly accumulates links from each city page.
"""
from typing import List
from bs4 import BeautifulSoup

from .base import BaseConnector, ConnectorResult, RawHackathon

# Popular tech cities for hackathon discovery
CITIES = [
    "san-francisco", "bengaluru", "london", "new-york",
    "pune", "delhi", "mumbai", "hyderabad", "chennai",
]

HACKATHON_KEYWORDS = {"hackathon", "hack", "build", "buildathon", "code", "sprint", "thon"}


def _is_hackathon_title(title: str) -> bool:
    """Check if the title is likely a hackathon (not a regular meetup)."""
    tl = title.lower()
    return any(kw in tl for kw in HACKATHON_KEYWORDS)


def _parse_city_page(html: str, city: str) -> list:
    """Extract hackathon event records from a Luma city page HTML."""
    soup = BeautifulSoup(html, "html.parser")
    records = []
    seen_slugs: set = set()

    for link in soup.select("a[href^='/']"):
        try:
            href = link.get("href", "")
            # Skip navigation/utility links
            if not href or href in ("/", ) or any(
                href.startswith(p) for p in ["/explore", "/search", "/create", "/home", "/calendar"]
            ):
                continue

            slug = href.lstrip("/")
            if len(slug) < 4 or " " in slug or slug in seen_slugs:
                continue
            seen_slugs.add(slug)

            # Extract title text
            title = link.get_text(separator=" ", strip=True).split('\n')[0].strip()
            if not title or len(title) < 5:
                continue

            # Only include events that are hackathon-related
            if not _is_hackathon_title(title):
                continue

            apply_url = f"https://lu.ma/{slug}"
            text_content = link.get_text()

            # Detect mode from text
            mode = "OFFLINE" if any(
                kw in text_content.lower()
                for kw in ("in person", "offline", "venue", "location")
            ) else "ONLINE"

            # Detect scope — Indian cities get INDIA scope
            scope = "INDIA" if city in ("bengaluru", "pune", "delhi", "mumbai", "hyderabad", "chennai") else "GLOBAL"

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
                sponsors=["lu.ma"],
            ))
        except Exception:
            continue

    return records


class LumaConnector(BaseConnector):
    SOURCE = "LUMA"
    SCOPE = "GLOBAL"

    def fetch(self) -> ConnectorResult:
        from ..zerocrawl_bridge import fetch_js_page

        all_records: List[RawHackathon] = []
        error = None
        seen_apply_urls: set = set()

        for city in CITIES:
            url = f"https://lu.ma/{city}"
            print(f"[{self.SOURCE}] Scraping city: {city} ({url})")

            try:
                # BUG FIX: Was accumulating after the loop; now correctly processes each city
                html = fetch_js_page(url, timeout=30)
                if not html:
                    print(f"[{self.SOURCE}] Empty response for city: {city}")
                    continue

                city_records = _parse_city_page(html, city)

                # Deduplicate across cities
                for rec in city_records:
                    if rec.apply_url not in seen_apply_urls:
                        seen_apply_urls.add(rec.apply_url)
                        all_records.append(rec)

                print(f"[{self.SOURCE}] City {city}: +{len(city_records)} events (unique so far: {len(all_records)})")

            except Exception as e:
                print(f"[{self.SOURCE}] Error for city {city}: {e}")
                error = str(e)
                continue

        print(f"[{self.SOURCE}] Total unique hackathons: {len(all_records)}")
        status = "SUCCESS" if all_records else ("PARTIAL" if error else "FAILED")
        return ConnectorResult(source=self.SOURCE, records=all_records, status=status, error=error)
