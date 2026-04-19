"""
startup_india.py — Startup India / DPIIT connector.
Government hackathons, SIH, DPIIT challenges.
Method: httpx + BeautifulSoup.
"""
import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import BaseConnector, ConnectorResult, RawHackathon

URLS = [
    "https://www.startupindia.gov.in/content/sih/en/innov8/challenges.html",
    "https://sih.gov.in",
]
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; 1ph-bot/1.0)"}


class StartupIndiaConnector(BaseConnector):
    SOURCE = "STARTUP_INDIA"
    SCOPE = "INDIA"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=5, max=30))
    def _get(self, url: str) -> str:
        with httpx.Client(timeout=20, headers=HEADERS, follow_redirects=True) as client:
            r = client.get(url)
            r.raise_for_status()
            return r.text

    def _parse_page(self, html: str, source_url: str) -> list:
        soup = BeautifulSoup(html, "html.parser")
        records = []

        # Try multiple card selectors government sites use
        cards = (
            soup.select(".challenge-card")
            or soup.select(".initiative-card")
            or soup.select(".card")
            or soup.select("article")
        )

        for card in cards:
            try:
                title_el = (
                    card.select_one("h2") or card.select_one("h3")
                    or card.select_one(".title") or card.select_one(".heading")
                )
                if not title_el:
                    continue

                title = title_el.get_text(strip=True)
                if not title or len(title) < 5:
                    continue

                link_el = card.select_one("a[href]")
                if link_el:
                    href = link_el.get("href", "")
                    apply_url = href if href.startswith("http") else f"https://www.startupindia.gov.in{href}"
                else:
                    apply_url = source_url

                desc_el = card.select_one("p") or card.select_one(".description")
                description = desc_el.get_text(strip=True)[:500] if desc_el else None

                records.append(RawHackathon(
                    source_id=apply_url,
                    title=title,
                    organizer_name="Startup India / DPIIT",
                    apply_url=apply_url,
                    registration_close="2099-12-31",
                    description=description,
                    scope="INDIA",
                    mode="ONLINE",
                    eligibility="OPEN",
                    sponsors=["DPIIT", "Government of India"],
                ))
            except Exception:
                continue

        return records

    def fetch(self) -> ConnectorResult:
        records = []
        error = None

        for url in URLS:
            try:
                html = self._get(url)
                page_records = self._parse_page(html, url)
                records.extend(page_records)
            except Exception as e:
                error = str(e)
                continue

        # Deduplicate by apply_url within this connector
        seen = set()
        unique = []
        for r in records:
            if r.apply_url not in seen:
                seen.add(r.apply_url)
                unique.append(r)

        status = "SUCCESS" if unique else ("PARTIAL" if error else "FAILED")
        return ConnectorResult(source=self.SOURCE, records=unique, status=status, error=error)
