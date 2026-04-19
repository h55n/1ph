"""
hackerearth.py — HackerEarth public API connector.
"""
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import BaseConnector, ConnectorResult, RawHackathon

API_URL = "https://www.hackerearth.com/api/v2/challenges/"
HEADERS = {"Accept": "application/json", "User-Agent": "1ph-pipeline/1.0"}


class HackerEarthConnector(BaseConnector):
    SOURCE = "HACKEREARTH"
    SCOPE = "GLOBAL"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=20))
    def _get(self, offset: int) -> dict:
        with httpx.Client(timeout=20, headers=HEADERS) as client:
            r = client.get(API_URL, params={
                "limit": 20,
                "offset": offset,
                "type": "HACKATHON",
                "status": "UPCOMING,ONGOING",
            })
            r.raise_for_status()
            return r.json()

    def fetch(self) -> ConnectorResult:
        records = []
        offset = 0

        while True:
            try:
                data = self._get(offset)
            except Exception as e:
                status = "PARTIAL" if records else "FAILED"
                return ConnectorResult(source=self.SOURCE, records=records, status=status, error=str(e))

            challenges = data.get("response", {}).get("data", {}).get("results", [])
            if not challenges:
                break

            for ch in challenges:
                try:
                    title = ch.get("title", "")
                    url = ch.get("url", "")
                    if not title or not url:
                        continue

                    close_raw = ch.get("registration_end_date") or ch.get("end_date") or ""
                    close_date = close_raw[:10] if close_raw else "2099-12-31"

                    prize_raw = ch.get("prize_amount") or ch.get("total_prize") or 0
                    try:
                        prize = float(str(prize_raw).replace(",", "").replace("$", "")) if prize_raw else None
                    except ValueError:
                        prize = None

                    tags_raw = ch.get("tags") or []
                    tags = [t.get("name", "") for t in tags_raw if isinstance(t, dict)][:5]

                    records.append(RawHackathon(
                        source_id=str(ch.get("id", url)),
                        title=title,
                        organizer_name=ch.get("company_name") or "HackerEarth",
                        apply_url=url,
                        registration_close=close_date,
                        event_start=ch.get("start_date", "")[:10] if ch.get("start_date") else None,
                        description=ch.get("description", "")[:500] if ch.get("description") else None,
                        prize_pool=prize,
                        theme_tags=tags,
                        mode="ONLINE",
                        scope="GLOBAL",
                        organizer_logo_url=ch.get("company_logo_url"),
                    ))
                except Exception:
                    continue

            if len(challenges) < 20:
                break
            offset += 20

        status = "SUCCESS" if records else "PARTIAL"
        return ConnectorResult(source=self.SOURCE, records=records, status=status)
