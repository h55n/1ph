"""
toplang.py — Topcoder connector.
Scrapes Topcoder's public challenge listings for current competition opportunities.
"""
import re
from datetime import datetime

from .base import BaseConnector, ConnectorResult, RawHackathon

LIST_URL = "https://www.topcoder.com/challenges"
MONTHS = {
    "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
    "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12",
}


def _parse_end_date(text: str) -> str:
    m = re.search(r"Ends\s+([A-Z]{3})\s+(\d{1,2})", text, re.I)
    if not m:
        return "2099-12-31"
    month = MONTHS.get(m.group(1).lower())
    if not month:
        return "2099-12-31"
    day = int(m.group(2))
    year = datetime.now().year
    if int(month) < datetime.now().month - 1:
        year += 1
    return f"{year}-{month}-{day:02d}"


class TopLangConnector(BaseConnector):
    SOURCE = "TOPLANG"
    SCOPE = "GLOBAL"

    def fetch(self) -> ConnectorResult:
        from playwright.sync_api import sync_playwright

        records = []
        error = None

        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                ctx = browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                    ),
                    viewport={"width": 1366, "height": 768},
                )
                page = ctx.new_page()

                try:
                    page.goto(LIST_URL, timeout=60000, wait_until="domcontentloaded")
                    page.wait_for_timeout(5000)
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(2500)

                    seen = set()
                    links = page.query_selector_all("a[href*='/challenges/']")
                    for link in links:
                        try:
                            href = link.get_attribute("href") or ""
                            if not href:
                                continue
                            clean_href = href.split("?")[0]
                            if "/challenges/" not in clean_href:
                                continue
                            if clean_href in seen:
                                continue
                            seen.add(clean_href)

                            text = link.inner_text().strip().replace("\n", " ")
                            title = text.split("Ends ")[0].strip() or clean_href.rstrip("/").split("/")[-1]
                            if not title or len(title) < 5:
                                continue

                            container = link.locator("xpath=ancestor::*[self::article or self::div][1]")
                            container_text = ""
                            try:
                                container_text = container.inner_text(timeout=3000).strip()
                            except Exception:
                                container_text = text

                            records.append(RawHackathon(
                                source_id=clean_href.rstrip("/").split("/")[-1],
                                title=title,
                                organizer_name="Topcoder",
                                apply_url=f"https://www.topcoder.com{clean_href}" if clean_href.startswith("/") else clean_href,
                                registration_close=_parse_end_date(container_text or text),
                                description=(container_text or text)[:500],
                                theme_tags=["Competitive Programming", "Algorithms"],
                                mode="ONLINE",
                                scope="GLOBAL",
                                sponsors=["Topcoder"],
                            ))
                        except Exception:
                            continue

                except Exception as e:
                    error = str(e)
                finally:
                    browser.close()
        except Exception as e:
            error = str(e)

        status = "SUCCESS" if records else ("PARTIAL" if error else "FAILED")
        return ConnectorResult(source=self.SOURCE, records=records, status=status, error=error)
