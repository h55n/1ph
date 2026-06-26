"""
startup_grants_india.py — StartupGrantsIndia connector.
Scrapes https://www.startupgrantsindia.com/competitions — India's startup
competitions, hackathons, pitch contests, and innovation challenges.
Method: httpx + BeautifulSoup (server-rendered HTML).
"""
import re
import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import BaseConnector, ConnectorResult, RawHackathon

BASE_URL = "https://www.startupgrantsindia.com"
LIST_URL = f"{BASE_URL}/competitions"
PAGES_TO_SCRAPE = 6  # scrape a wider set of pages for better coverage

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

PRIZE_RE = re.compile(r"[\d,]+(?:\.\d+)?")


def _parse_prize(text: str):
    """Parse prize text → float. Handles ₹, L/Lakh shorthand."""
    if not text:
        return None
    text = text.replace(",", "").replace("₹", "").replace("$", "").strip()
    nums = PRIZE_RE.findall(text)
    if not nums:
        return None
    try:
        v = float(nums[0])
        # Convert lakh shorthand: "5 Lakhs" → 500000
        if any(x in text.lower() for x in ["lakh", " l", "lac"]):
            if v < 10000:
                v *= 100_000
        return v
    except ValueError:
        return None


class StartupGrantsIndiaConnector(BaseConnector):
    SOURCE = "STARTUP_INDIA"
    SCOPE = "INDIA"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=20))
    def _get(self, url: str) -> str:
        with httpx.Client(timeout=30, headers=HEADERS, follow_redirects=True) as client:
            r = client.get(url)
            r.raise_for_status()
            return r.text

    def _get_detail_description(self, detail_url: str) -> str | None:
        """Fetch the competition detail page and extract a full description."""
        try:
            html = self._get(detail_url)
            soup = BeautifulSoup(html, "html.parser")

            # Try common description containers on startupgrantsindia detail pages
            desc_el = (
                soup.select_one("[class*='description']")
                or soup.select_one("[class*='about']")
                or soup.select_one("[class*='content'] p")
                or soup.select_one("article p")
                or soup.select_one(".prose")
                or soup.select_one("main p")
            )
            if desc_el:
                # Get all sibling/child paragraphs for a richer description
                parent = desc_el.parent
                if parent:
                    paras = parent.find_all("p")
                    if paras:
                        text = " ".join(p.get_text(strip=True) for p in paras[:6])
                        if len(text) > 80:
                            return text[:2000]
                text = desc_el.get_text(separator=" ", strip=True)
                if len(text) > 80:
                    return text[:2000]

            # Fallback: grab all <p> tags from main content area
            main = soup.select_one("main") or soup.body
            if main:
                paras = main.find_all("p")
                texts = [p.get_text(strip=True) for p in paras if len(p.get_text(strip=True)) > 40]
                if texts:
                    return " ".join(texts[:5])[:2000]
        except Exception as e:
            print(f"[{self.SOURCE}] Detail fetch failed for {detail_url}: {e}")
        return None

    def _parse_page(self, html: str) -> list:
        soup = BeautifulSoup(html, "html.parser")
        records = []

        # Each competition is a link with /competitions/<slug> and has a h2 title
        # Pattern from HTML: each card is an <a> wrapping the card content
        competition_links = soup.select("a[href*='/competitions/']")
        seen = set()

        for link in competition_links:
            try:
                href = link.get("href", "")
                if not href or "/competitions/" not in href:
                    continue
                # Skip filter/type/mode navigation links
                if any(x in href for x in ["/type/", "/mode/", "/deadline/", "/prize/"]):
                    continue

                apply_url = href if href.startswith("http") else f"{BASE_URL}{href}"
                slug_part = href.rstrip("/").split("/competitions/")[-1]
                if not slug_part or slug_part in seen:
                    continue
                seen.add(slug_part)

                # Title: find h2 or h3 inside the link
                title_el = link.find(["h2", "h3"]) or link.find(attrs={"class": re.compile(r"title|heading|name", re.I)})
                if title_el:
                    title = title_el.get_text(strip=True)
                else:
                    # Use slug as title fallback
                    title = slug_part.replace("-", " ").title()

                if not title or len(title) < 5:
                    continue

                # Organizer
                org_el = link.find(attrs={"class": re.compile(r"org|organiz|host|company|school|instit", re.I)})
                org = org_el.get_text(strip=True) if org_el else "StartupGrantsIndia"

                # Prize text
                prize_el = link.find(attrs={"class": re.compile(r"prize|reward|amount|fund", re.I)})
                prize_text = prize_el.get_text(strip=True) if prize_el else ""
                prize = _parse_prize(prize_text)

                # Description (short blurb visible on listing card)
                desc_el = link.find("p") or link.find(attrs={"class": re.compile(r"desc|summary|blurb|excerpt", re.I)})
                card_desc = desc_el.get_text(strip=True)[:500] if desc_el else None

                # Mode detection from text
                text_content = link.get_text(" ", strip=True).lower()
                if "online" in text_content:
                    mode = "ONLINE"
                elif "in-person" in text_content or "offline" in text_content or "campus" in text_content:
                    mode = "OFFLINE"
                else:
                    mode = "ONLINE"  # SGI is mostly online

                records.append({
                    "source_id": slug_part,
                    "title": title,
                    "organizer_name": org,
                    "apply_url": apply_url,
                    "card_desc": card_desc,
                    "prize": prize,
                    "mode": mode,
                })
            except Exception:
                continue

        return records

    def fetch(self) -> ConnectorResult:
        records = []
        error = None

        for page_num in range(1, PAGES_TO_SCRAPE + 1):
            try:
                url = LIST_URL if page_num == 1 else f"{LIST_URL}?page={page_num}"
                print(f"[{self.SOURCE}] Scraping page {page_num}: {url}")
                html = self._get(url)
                page_items = self._parse_page(html)
                print(f"[{self.SOURCE}] Page {page_num}: {len(page_items)} listings found")

                for item in page_items:
                    # Fetch detail page for richer description
                    detail_desc = self._get_detail_description(item["apply_url"])
                    description = detail_desc or item["card_desc"]

                    records.append(RawHackathon(
                        source_id=f"sgi-{item['source_id']}",
                        title=item["title"],
                        organizer_name=item["organizer_name"],
                        apply_url=item["apply_url"],
                        registration_close="2099-12-31",
                        description=description,
                        prize_pool=item["prize"],
                        prize_currency="INR",
                        mode=item["mode"],
                        scope="INDIA",
                        sponsors=["StartupGrantsIndia"],
                    ))
            except Exception as e:
                error = str(e)
                print(f"[{self.SOURCE}] Page {page_num} error: {e}")
                continue

        # Deduplicate by apply_url
        seen: set = set()
        unique = []
        for r in records:
            if r.apply_url not in seen:
                seen.add(r.apply_url)
                unique.append(r)

        print(f"[{self.SOURCE}] Total unique: {len(unique)}")
        status = "SUCCESS" if unique else ("PARTIAL" if error else "FAILED")
        return ConnectorResult(source=self.SOURCE, records=unique, status=status, error=error)
