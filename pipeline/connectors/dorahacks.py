"""
dorahacks.py - DoraHacks connector.
Uses DoraHacks public API with WAF-bypass headers.
Falls back to Playwright if the API is rate-limited.
"""
import random
import re

import httpx

from .base import BaseConnector, ConnectorResult, RawHackathon

LIST_URL = "https://dorahacks.io/hackathon"

# Working API endpoint (tested - returns 808 hackathons with browser Referer header)
API_URL = "https://dorahacks.io/api/hackathon/?limit=50&offset={offset}&is_active=true&ordering=-created"


def _parse_prize(text: str):
    if not text:
        return None
    text = str(text).replace(",", "").replace("$", "").replace("USD", "").strip()
    nums = re.findall(r"\d+(?:\.\d+)?", text)
    if nums:
        try:
            return float(nums[0])
        except ValueError:
            pass
    return None


class DoraHacksConnector(BaseConnector):
    SOURCE = "DORAHACKS"
    SCOPE = "GLOBAL"

    def _try_api(self) -> list:
        """Try DoraHacks REST API — works with browser Referer header."""
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://dorahacks.io/hackathon",
        }
        try:
            records = []
            seen: set = set()
            next_url = API_URL.format(offset=0)
            max_pages = 40  # 40 * 10 = 400 hackathons max
            page_num = 0
            with httpx.Client(timeout=25, follow_redirects=True, headers=headers) as client:
                while next_url and page_num < max_pages:
                    try:
                        r = client.get(next_url)
                        if r.status_code != 200:
                            print(f"[{self.SOURCE}] API HTTP {r.status_code}, stopping")
                            break
                        data = r.json()
                    except Exception as e:
                        print(f"[{self.SOURCE}] API parse error: {e}")
                        break

                    # DoraHacks wraps response in multiple ways
                    items = (
                        data.get("results")
                        or data.get("data")
                        or []
                    )
                    if not items:
                        break

                    for item in items:
                        try:
                            title = (item.get("title") or item.get("name") or "").strip()
                            if not title:
                                continue

                            # DoraHacks uses `uname` as slug, fallback to `id`
                            slug_or_id = str(item.get("uname") or item.get("slug") or item.get("id") or "")
                            if not slug_or_id or slug_or_id in seen:
                                continue
                            seen.add(slug_or_id)

                            apply_url = f"https://dorahacks.io/hackathon/{slug_or_id}"
                            prize_raw = item.get("bonus_price") or item.get("prize_pool") or item.get("total_prize")
                            prize = _parse_prize(str(prize_raw)) if prize_raw else None

                            description = (item.get("description") or item.get("intro") or "")
                            if description:
                                description = str(description)[:500]
                            else:
                                description = None

                            # end_time is a Unix epoch integer
                            reg_close = None
                            end_epoch = item.get("end_time") or item.get("registration_end")
                            if end_epoch:
                                try:
                                    from datetime import datetime, timezone
                                    reg_close = datetime.fromtimestamp(int(end_epoch), tz=timezone.utc).strftime("%Y-%m-%d")
                                except Exception:
                                    reg_close = None

                            # Organization is a nested object
                            org_obj = item.get("organization") or {}
                            org = (org_obj.get("name") if isinstance(org_obj, dict) else None) or "DoraHacks"

                            records.append(RawHackathon(
                                source_id=f"dh-{slug_or_id}",
                                title=title,
                                organizer_name=org,
                                apply_url=apply_url,
                                registration_close=reg_close,
                                prize_pool=prize,
                                prize_currency="USD",
                                description=description,
                                mode="ONLINE",
                                scope="GLOBAL",
                            ))
                        except Exception:
                            continue

                    page_num += 1
                    # Follow the `next` URL from the response
                    raw_next = data.get("next") or ""
                    if raw_next:
                        # Ensure HTTPS (API sometimes returns http)
                        next_url = raw_next.replace("http://dorahacks.io", "https://dorahacks.io")
                    else:
                        break

            if records:
                print(f"[{self.SOURCE}] API returned {len(records)} records")
                return records

        except Exception as e:
            print(f"[{self.SOURCE}] API attempt failed: {e}")
        return []

    def _try_playwright(self) -> list:
        """Playwright fallback — extract data from JSON embedded in <script> tags."""
        from playwright.sync_api import sync_playwright

        records = []
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                ctx = browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                    ),
                    viewport={"width": 1280, "height": 900},
                )
                page = ctx.new_page()

                # Intercept XHR responses to capture API data before WAF blocks it
                api_data: list = []

                def handle_response(response):
                    try:
                        if "dorahacks.io/api/hackathon" in response.url and response.status == 200:
                            body = response.json()
                            items = (
                                body.get("results")
                                or body.get("data")
                                or []
                            )
                            if items:
                                api_data.extend(items)
                    except Exception:
                        pass

                page.on("response", handle_response)

                try:
                    print(f"[{self.SOURCE}] Playwright: Navigating to {LIST_URL}...")
                    page.goto(LIST_URL, timeout=60000, wait_until="domcontentloaded")
                    page.wait_for_timeout(6000)

                    for _ in range(4):
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        page.wait_for_timeout(random.randint(1500, 2500))

                    if api_data:
                        print(f"[{self.SOURCE}] Intercepted {len(api_data)} API items via Playwright")
                        seen: set = set()
                        for item in api_data:
                            try:
                                title = (item.get("title") or item.get("name") or "").strip()
                                slug_or_id = str(item.get("slug") or item.get("id") or "")
                                if not title or not slug_or_id or slug_or_id in seen:
                                    continue
                                seen.add(slug_or_id)
                                apply_url = f"https://dorahacks.io/hackathon/{slug_or_id}"
                                prize_raw = item.get("prize_pool") or item.get("total_prize")
                                prize = _parse_prize(str(prize_raw)) if prize_raw else None
                                end_time = item.get("end_time") or item.get("registration_end")
                                reg_close = str(end_time)[:10] if end_time else None
                                records.append(RawHackathon(
                                    source_id=f"dh-{slug_or_id}",
                                    title=title,
                                    organizer_name=(item.get("organizer_name") or "DoraHacks").strip(),
                                    apply_url=apply_url,
                                    registration_close=reg_close,
                                    prize_pool=prize,
                                    prize_currency="USD",
                                    mode="ONLINE",
                                    scope="GLOBAL",
                                ))
                            except Exception:
                                continue
                    else:
                        # Last resort: grab card links
                        links = page.query_selector_all("a[href*='/hackathon/']")
                        seen2: set = set()
                        for link in links:
                            try:
                                href = link.get_attribute("href") or ""
                                if not href or href in seen2 or href == "/hackathon":
                                    continue
                                seen2.add(href)
                                apply_url = href if href.startswith("http") else f"https://dorahacks.io{href}"
                                title_el = link.query_selector("h2, h3, [class*='title'], [class*='name']")
                                title = title_el.inner_text().strip() if title_el else ""
                                if not title or len(title) < 3:
                                    title = href.rstrip("/").split("/")[-1].replace("-", " ").title()
                                if not title:
                                    continue
                                slug = href.rstrip("/").split("/")[-1]
                                records.append(RawHackathon(
                                    source_id=f"dh-{slug}",
                                    title=title,
                                    organizer_name="DoraHacks",
                                    apply_url=apply_url,
                                    registration_close=None,
                                    mode="ONLINE",
                                    scope="GLOBAL",
                                ))
                            except Exception:
                                continue

                    print(f"[{self.SOURCE}] Playwright collected {len(records)} records")
                except Exception as e:
                    print(f"[{self.SOURCE}] Playwright error: {e}")
                finally:
                    browser.close()
        except Exception as e:
            print(f"[{self.SOURCE}] Playwright outer error: {e}")

        return records

    def fetch(self) -> ConnectorResult:
        records = self._try_api()
        if not records:
            records = self._try_playwright()

        status = "SUCCESS" if records else "FAILED"
        return ConnectorResult(source=self.SOURCE, records=records, status=status, error=None)
