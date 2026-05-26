"""
devpost.py — Devpost connector.
Method: ZeroCrawl (auto-mode with TLS fingerprinting + Playwright fallback).
Handles Cloudflare and JS rendering automatically.
"""
import re
from bs4 import BeautifulSoup

from .base import BaseConnector, ConnectorResult, RawHackathon

LIST_URL = "https://devpost.com/hackathons?challenge_type[]=online&status[]=open&status[]=upcoming"
MAX_PAGES = 4


def _parse_prize(text: str):
    if not text:
        return None
    text = text.replace(",", "").replace("$", "").replace("USD", "").strip()
    nums = re.findall(r"\d+(?:\.\d+)?", text)
    if nums:
        try:
            return float(nums[0])
        except ValueError:
            pass
    return None


def _parse_page(html: str, records: list) -> bool:
    """Parse one page of Devpost hackathon listings. Returns True if cards found."""
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("article.challenge-listing, .challenge-listing")

    if not cards:
        return False

    for card in cards:
        try:
            title_el = card.select_one("h2, .challenge-title, .title")
            link_el = card.select_one("a[href*='/hackathons/']")
            if not title_el or not link_el:
                continue

            title = title_el.get_text(strip=True)
            apply_url = link_el.get("href", "")
            if not apply_url.startswith("http"):
                apply_url = f"https://devpost.com{apply_url}"

            prize_el = card.select_one(".prize, .prize-amount")
            prize_text = prize_el.get_text(strip=True) if prize_el else ""
            prize = _parse_prize(prize_text)

            deadline_el = card.select_one(".submission-period, .date")
            deadline_text = deadline_el.get_text(strip=True) if deadline_el else ""

            tags_els = card.select(".theme, .tag")
            tags = [t.get_text(strip=True) for t in tags_els[:5]]

            org_el = card.select_one(".host-label, .organizer")
            org = org_el.get_text(strip=True) if org_el else "Devpost"

            records.append(RawHackathon(
                source_id=apply_url.split("/")[-1] or apply_url,
                title=title,
                organizer_name=org,
                apply_url=apply_url,
                registration_close="2099-12-31",
                description=deadline_text[:500] if deadline_text else None,
                prize_pool=prize,
                prize_currency="USD",
                theme_tags=tags,
                mode="ONLINE",
                scope="GLOBAL",
            ))
        except Exception:
            continue

    return True


class DevpostConnector(BaseConnector):
    SOURCE = "DEVPOST"
    SCOPE = "GLOBAL"

    def fetch(self) -> ConnectorResult:
        from ..zerocrawl_bridge import fetch_html

        records = []
        error = None

        try:
            print(f"[{self.SOURCE}] Fetching {LIST_URL} via ZeroCrawl...")
            # Devpost has Cloudflare — use auto mode which escalates to browser if blocked
            html = fetch_html(LIST_URL, mode="auto", timeout=90)

            if not html:
                return ConnectorResult(
                    source=self.SOURCE, records=[], status="FAILED",
                    error="ZeroCrawl returned empty response"
                )

            found = _parse_page(html, records)
            if not found:
                print(f"[{self.SOURCE}] No cards found in first page — trying browser mode")
                html = fetch_html(LIST_URL, mode="browser", timeout=90, force_refresh=True)
                _parse_page(html, records)

            print(f"[{self.SOURCE}] Page 1: {len(records)} records")

            # Try pagination via URL manipulation (Devpost uses ?page=N)
            for page_num in range(2, MAX_PAGES + 1):
                try:
                    page_url = f"{LIST_URL}&page={page_num}"
                    page_html = fetch_html(page_url, mode="auto", timeout=60)
                    if not page_html:
                        break
                    prev_count = len(records)
                    _parse_page(page_html, records)
                    new_count = len(records) - prev_count
                    print(f"[{self.SOURCE}] Page {page_num}: +{new_count} records")
                    if new_count == 0:
                        break
                except Exception as e:
                    print(f"[{self.SOURCE}] Page {page_num} error: {e}")
                    break

        except Exception as e:
            error = str(e)
            print(f"[{self.SOURCE}] Error: {e}")

        print(f"[{self.SOURCE}] Total: {len(records)} records")
        status = "SUCCESS" if records else ("PARTIAL" if error else "FAILED")
        return ConnectorResult(source=self.SOURCE, records=records, status=status, error=error)
