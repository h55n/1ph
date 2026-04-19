"""
mlh.py — Major League Hacking connector.
Method: httpx + BeautifulSoup (static HTML, no browser needed).
"""
import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import BaseConnector, ConnectorResult, RawHackathon

URL = "https://mlh.io/seasons/2025/events"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}


class MLHConnector(BaseConnector):
    SOURCE = "MLH"
    SCOPE = "GLOBAL"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=20))
    def _get_html(self) -> str:
        with httpx.Client(timeout=20, headers=HEADERS, follow_redirects=True) as client:
            r = client.get(URL)
            r.raise_for_status()
            return r.text

    def fetch(self) -> ConnectorResult:
        html = self._get_html()
        soup = BeautifulSoup(html, "html.parser")
        records = []

        for event in soup.select("div.event"):
            try:
                title_el = event.select_one(".event-name")
                date_el = event.select_one(".event-date")
                link_el = event.select_one("a.event-link") or event.select_one("a")
                loc_el = event.select_one(".event-location")

                if not title_el or not link_el:
                    continue

                title = title_el.get_text(strip=True)
                apply_url = link_el.get("href", "").strip()
                if not apply_url or not apply_url.startswith("http"):
                    continue

                date_text = date_el.get_text(strip=True) if date_el else ""
                location = loc_el.get_text(strip=True) if loc_el else ""
                mode = "ONLINE" if "online" in location.lower() else "OFFLINE"

                records.append(RawHackathon(
                    source_id=apply_url,
                    title=title,
                    organizer_name="Major League Hacking",
                    apply_url=apply_url,
                    registration_close="2099-12-31",  # MLH doesn't show reg close; swept daily
                    description=f"MLH event. {date_text}. {location}".strip(". "),
                    mode=mode,
                    scope="GLOBAL",
                    theme_tags=["Open"],
                    eligibility="STUDENTS",
                    sponsors=["MLH"],
                ))
            except Exception:
                continue

        status = "SUCCESS" if records else "PARTIAL"
        return ConnectorResult(source=self.SOURCE, records=records, status=status)
