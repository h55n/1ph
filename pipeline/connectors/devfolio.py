"""
devfolio.py — Devfolio GraphQL API connector. India-focused.
"""
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import BaseConnector, ConnectorResult, RawHackathon

GQL_URL = "https://api.devfolio.co/api/search/hackathons"
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "1ph-pipeline/1.0",
}
GQL_BODY = {
    "query": "",
    "size": 50,
    "from": 0,
    "filters": {"status": ["open", "upcoming"]},
}


class DevfolioConnector(BaseConnector):
    SOURCE = "DEVFOLIO"
    SCOPE = "INDIA"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=20))
    def _get(self, offset: int) -> dict:
        body = {**GQL_BODY, "from": offset}
        with httpx.Client(timeout=25, headers=HEADERS) as client:
            r = client.post(GQL_URL, json=body)
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

            hits = data.get("hits", {}).get("hits", [])
            if not hits:
                break

            for hit in hits:
                src = hit.get("_source", {})
                try:
                    title = src.get("name") or src.get("title", "")
                    slug = src.get("slug", "")
                    if not title or not slug:
                        continue

                    apply_url = f"https://devfolio.co/hackathons/{slug}"
                    close_raw = src.get("submission_deadline") or src.get("ends_at") or ""
                    close_date = close_raw[:10] if close_raw else "2099-12-31"

                    prize_raw = src.get("total_prizes") or src.get("prize_amount") or 0
                    try:
                        prize = float(str(prize_raw).replace(",", "").replace("₹", "").replace("$", "")) if prize_raw else None
                    except ValueError:
                        prize = None

                    currency = "INR" if src.get("currency") == "INR" or prize_raw and "₹" in str(prize_raw) else "USD"
                    tags = src.get("themes") or src.get("tags") or []
                    tags = [str(t) for t in tags][:5]

                    mode_raw = src.get("type") or src.get("mode") or ""
                    if "online" in mode_raw.lower():
                        mode = "ONLINE"
                    elif "offline" in mode_raw.lower() or "in-person" in mode_raw.lower():
                        mode = "OFFLINE"
                    else:
                        mode = "ONLINE"

                    records.append(RawHackathon(
                        source_id=slug,
                        title=title,
                        organizer_name=src.get("organization") or src.get("team_name") or "Devfolio",
                        apply_url=apply_url,
                        registration_close=close_date,
                        event_start=src.get("starts_at", "")[:10] if src.get("starts_at") else None,
                        description=src.get("tagline") or src.get("description", "")[:500],
                        prize_pool=prize,
                        prize_currency=currency,
                        theme_tags=tags,
                        mode=mode,
                        scope="INDIA",
                        organizer_logo_url=src.get("logo"),
                    ))
                except Exception:
                    continue

            if len(hits) < 50:
                break
            offset += 50

        status = "SUCCESS" if records else "PARTIAL"
        return ConnectorResult(source=self.SOURCE, records=records, status=status)
