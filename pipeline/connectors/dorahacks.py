"""
dorahacks.py — DoraHacks public REST API connector.
No browser needed.
"""
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import BaseConnector, ConnectorResult, RawHackathon

API_URL = "https://dorahacks.io/api/hackathon/list"
HEADERS = {"Accept": "application/json", "User-Agent": "1ph-pipeline/1.0"}


class DoraHacksConnector(BaseConnector):
    SOURCE = "DORAHACKS"
    SCOPE = "GLOBAL"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=20))
    def _get_page(self, offset: int) -> dict:
        with httpx.Client(timeout=20, headers=HEADERS) as client:
            r = client.get(API_URL, params={"limit": 50, "offset": offset, "status": "open"})
            r.raise_for_status()
            return r.json()

    def fetch(self) -> ConnectorResult:
        records = []
        offset = 0

        while True:
            try:
                data = self._get_page(offset)
            except Exception as e:
                status = "PARTIAL" if records else "FAILED"
                return ConnectorResult(source=self.SOURCE, records=records, status=status, error=str(e))

            items = data.get("data", data.get("list", data.get("hackathons", [])))
            if not items:
                break

            for item in items:
                try:
                    title = item.get("title") or item.get("name", "")
                    if not title:
                        continue

                    source_id = str(item.get("id") or item.get("buidl_id", ""))
                    slug = item.get("slug") or item.get("url", "")
                    apply_url = (
                        f"https://dorahacks.io/hackathon/{slug}"
                        if slug and not slug.startswith("http")
                        else slug or f"https://dorahacks.io/hackathon/{source_id}"
                    )

                    close_date = (
                        item.get("registration_end")
                        or item.get("end_time")
                        or item.get("deadline")
                        or "2099-12-31"
                    )
                    if close_date and len(close_date) > 10:
                        close_date = close_date[:10]

                    prize_raw = item.get("prize_pool") or item.get("total_prize") or 0
                    try:
                        prize = float(str(prize_raw).replace(",", "").replace("$", "")) if prize_raw else None
                    except ValueError:
                        prize = None

                    tags = item.get("tags") or item.get("tracks") or []
                    if isinstance(tags, list):
                        tags = [str(t) for t in tags][:5]

                    records.append(RawHackathon(
                        source_id=source_id,
                        title=title,
                        organizer_name=item.get("organizer") or item.get("org_name") or "DoraHacks",
                        apply_url=apply_url,
                        registration_close=close_date,
                        event_start=item.get("start_time", "")[:10] if item.get("start_time") else None,
                        description=item.get("description", "")[:500] if item.get("description") else None,
                        prize_pool=prize,
                        prize_currency="USD",
                        theme_tags=tags,
                        mode="ONLINE",
                        scope="GLOBAL",
                        organizer_logo_url=item.get("logo_url") or item.get("org_logo"),
                    ))
                except Exception:
                    continue

            if len(items) < 50:
                break
            offset += 50

        status = "SUCCESS" if records else "PARTIAL"
        return ConnectorResult(source=self.SOURCE, records=records, status=status)
