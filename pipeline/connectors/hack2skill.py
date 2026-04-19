"""
hack2skill.py — Hack2Skill connector. India's largest hackathon aggregator.
Method: httpx + BeautifulSoup.
"""
import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import BaseConnector, ConnectorResult, RawHackathon

BASE_URL = "https://hack2skill.com"
LIST_URL = "https://hack2skill.com/hackathons"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "Chrome/124.0 Safari/537.36"
    )
}


class Hack2SkillConnector(BaseConnector):
    SOURCE = "HACK2SKILL"
    SCOPE = "INDIA"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=20))
    def _get(self, url: str) -> str:
        with httpx.Client(timeout=20, headers=HEADERS, follow_redirects=True) as client:
            r = client.get(url)
            r.raise_for_status()
            return r.text

    def fetch(self) -> ConnectorResult:
        records = []
        try:
            html = self._get(LIST_URL)
        except Exception as e:
            return ConnectorResult(source=self.SOURCE, records=[], status="FAILED", error=str(e))

        soup = BeautifulSoup(html, "html.parser")

        # Hack2Skill uses various card selectors — try all common ones
        cards = (
            soup.select(".hackathon-card")
            or soup.select(".event-card")
            or soup.select(".card-body")
            or soup.select("article.hackathon")
        )

        for card in cards:
            try:
                title_el = (
                    card.select_one("h2") or card.select_one("h3")
                    or card.select_one(".title") or card.select_one(".hackathon-title")
                )
                link_el = card.select_one("a[href]")

                if not title_el or not link_el:
                    continue

                title = title_el.get_text(strip=True)
                href = link_el.get("href", "")
                if not href:
                    continue
                apply_url = href if href.startswith("http") else f"{BASE_URL}{href}"

                date_el = card.select_one(".date") or card.select_one(".deadline") or card.select_one("time")
                date_text = date_el.get_text(strip=True) if date_el else ""

                prize_el = card.select_one(".prize") or card.select_one(".reward")
                prize_text = prize_el.get_text(strip=True) if prize_el else ""
                prize = None
                if prize_text:
                    import re
                    nums = re.findall(r"[\d,]+", prize_text.replace(",", ""))
                    if nums:
                        try:
                            prize = float(nums[0])
                        except ValueError:
                            pass

                desc_el = card.select_one("p") or card.select_one(".description")
                description = desc_el.get_text(strip=True)[:500] if desc_el else None

                records.append(RawHackathon(
                    source_id=apply_url,
                    title=title,
                    organizer_name="Hack2Skill",
                    apply_url=apply_url,
                    registration_close="2099-12-31",
                    description=description,
                    prize_pool=prize,
                    prize_currency="INR",
                    mode="ONLINE",
                    scope="INDIA",
                ))
            except Exception:
                continue

        status = "SUCCESS" if records else "PARTIAL"
        return ConnectorResult(source=self.SOURCE, records=records, status=status)
