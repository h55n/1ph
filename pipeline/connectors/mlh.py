"""
mlh.py — Major League Hacking connector.
Method: httpx + BeautifulSoup (static HTML, no browser needed).
Parses the 2026 season events page.
"""
import re
import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import BaseConnector, ConnectorResult, RawHackathon

# MLH season URL — update this when season rolls over
SEASON_URLS = [
    "https://mlh.io/seasons/2025/events",
    "https://mlh.io/seasons/2026/events",
    "https://mlh.io/seasons/2027/events",
]
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

# Regex to extract date range from link text e.g. "APR 24 - 26" or "MAY 08 - 14"
DATE_RE = re.compile(
    r"(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\s+(\d+)\s*[-–]\s*(\d+)",
    re.IGNORECASE,
)

MONTH_MAP = {
    "JAN": "01", "FEB": "02", "MAR": "03", "APR": "04",
    "MAY": "05", "JUN": "06", "JUL": "07", "AUG": "08",
    "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12",
}

import datetime


def _parse_close_date(text: str) -> str:
    """Extract end date from the event text, return ISO YYYY-MM-DD or fallback."""
    m = DATE_RE.search(text)
    if m:
        month_str, _start_day, end_day = m.group(1).upper(), m.group(2), m.group(3)
        month_num = MONTH_MAP.get(month_str, "01")
        year = datetime.datetime.now().year
        # If month is before current month, assume next year
        if int(month_num) < datetime.datetime.now().month - 1:
            year += 1
        try:
            return f"{year}-{month_num}-{int(end_day):02d}"
        except Exception:
            pass
    return "2099-12-31"


class MLHConnector(BaseConnector):
    SOURCE = "MLH"
    SCOPE = "GLOBAL"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=20))
    def _get_html(self, url: str) -> str:
        with httpx.Client(timeout=20, headers=HEADERS, follow_redirects=True) as client:
            r = client.get(url)
            r.raise_for_status()
            return r.text

    def fetch(self) -> ConnectorResult:
        records = []
        error = None
        try:
            for url in SEASON_URLS:
                try:
                    html = self._get_html(url)
                except Exception as e:
                    error = str(e)
                    continue

                soup = BeautifulSoup(html, "html.parser")
                for a in soup.select("a[href]"):
                    href = a.get("href", "")
                    if "utm_source=mlh" not in href:
                        continue
                    apply_url = href.split("?")[0]
                    if not apply_url.startswith("http"):
                        continue

                    full_text = a.get_text(separator=" ", strip=True)
                    if not full_text:
                        continue

                    h4 = a.find_next_sibling("h4") or a.find("h4")
                    if h4:
                        title = h4.get_text(strip=True)
                    else:
                        text_before_date = DATE_RE.split(full_text)[0] if DATE_RE.search(full_text) else full_text
                        title = text_before_date.strip() or full_text[:80]

                    if not title or len(title) < 3:
                        continue

                    close_date = _parse_close_date(full_text)
                    mode = "ONLINE"
                    text_lower = full_text.lower()
                    if "digital" in text_lower or "online" in text_lower or "worldwide" in text_lower:
                        mode = "ONLINE"
                    elif "in-person" in text_lower or "in person" in text_lower:
                        mode = "OFFLINE"

                    description = f"MLH event. {full_text[:200]}".strip()
                    records.append(RawHackathon(
                        source_id=apply_url,
                        title=title,
                        organizer_name="Major League Hacking",
                        apply_url=apply_url,
                        registration_close=close_date,
                        description=description[:500],
                        mode=mode,
                        scope="GLOBAL",
                        theme_tags=["Open Innovation"],
                        eligibility="STUDENTS",
                        sponsors=["MLH"],
                    ))
        except Exception as e:
            error = str(e)

        unique = {r.apply_url: r for r in records}.values()
        status = "SUCCESS" if unique else ("PARTIAL" if error else "FAILED")
        return ConnectorResult(source=self.SOURCE, records=list(unique), status=status, error=error)
