"""
ZeroCrawl — Engine Orchestrator
Selects the right fetch mode, runs fallback chain, assembles ScrapeResult.
"""
from __future__ import annotations

import time
from typing import Any, Optional
from urllib.parse import urlparse

from loguru import logger

from ..anti_detection.robots import get_crawl_delay, is_allowed
from ..anti_detection.timing import get_default_controller
from ..extraction.pipeline import run_pipeline
from ..models import ScrapeOptions, ScrapeResult
from .detector import detect_js_required
from .fast import get_fast_fetcher
from .browser import BrowserFetcher
from .aggressive import AggressiveFetcher

_KNOWN_JS_REQUIRED = {
    "twitter.com", "x.com", "instagram.com", "facebook.com",
    "linkedin.com", "airbnb.com", "zillow.com", "realtor.com",
    "glassdoor.com", "indeed.com", "netflix.com", "discord.com",
}
_KNOWN_AGGRESSIVE = {"ticketmaster.com", "stubhub.com"}


class Orchestrator:
    def __init__(self):
        self._fast = get_fast_fetcher()
        self._browser = BrowserFetcher()
        self._aggressive = AggressiveFetcher()
        self._timing = get_default_controller()
        self._domain_history: dict[str, dict] = {}

    async def scrape(self, url: str, options: Optional[ScrapeOptions] = None) -> ScrapeResult:
        if options is None:
            options = ScrapeOptions()
        domain = _extract_domain(url)

        if options.respect_robots_txt and not is_allowed(url):
            return ScrapeResult(url=url, final_url=url, status="failed",
                                error="Disallowed by robots.txt", error_type="robots_disallowed")

        robots_delay = get_crawl_delay(url) if options.respect_robots_txt else None
        if robots_delay:
            import asyncio
            await asyncio.sleep(float(robots_delay))
        else:
            await self._timing.wait_for_domain(domain)

        mode = self._choose_mode(url, domain, options)
        return await self._execute_with_fallback(url, domain, options, mode)

    def _choose_mode(self, url, domain, options):
        if options.mode != "auto":
            return options.mode
        if domain in _KNOWN_AGGRESSIVE:
            return "aggressive"
        if domain in _KNOWN_JS_REQUIRED:
            return "browser"
        history = self._domain_history.get(domain, {})
        last = history.get("last_success_mode")
        if last and last != "fast":
            return last
        return "fast"

    async def _execute_with_fallback(self, url, domain, options, start_mode):
        modes = {"fast": ["fast", "browser", "aggressive"],
                 "browser": ["browser", "aggressive"],
                 "aggressive": ["aggressive"]}.get(start_mode, ["fast", "browser", "aggressive"])

        last_result = None
        for mode in modes:
            logger.debug(f"Trying mode={mode} for {url}")
            fetch_result = await self._fetch(url, mode, options)

            if fetch_result.get("error") and not fetch_result.get("html"):
                continue

            html = fetch_result.get("html", "")
            status_code = fetch_result.get("status_code", 200)
            detection = detect_js_required(html, status_code)

            if detection["has_captcha"]:
                return ScrapeResult(url=url, final_url=fetch_result.get("final_url", url),
                                    status="failed", mode=mode, timing_ms=fetch_result.get("timing_ms", 0),
                                    error="CAPTCHA detected", error_type="captcha")

            if detection["is_blocked"] and mode != modes[-1]:
                continue

            if detection["needs_browser"] and mode == "fast" and len(modes) > 1:
                continue

            result = run_pipeline(
                raw_html=html, url=url, final_url=fetch_result.get("final_url", url),
                fetch_mode=mode, timing_ms=fetch_result.get("timing_ms", 0),
                screenshot_b64=fetch_result.get("screenshot_b64"),
            )

            if result.status in ("success", "partial"):
                self._domain_history[domain] = {"last_success_mode": mode}
                return result
            last_result = result

        if last_result:
            last_result.status = "failed"
            return last_result
        return ScrapeResult(url=url, final_url=url, status="failed",
                            error="All modes exhausted", error_type="blocked")

    async def _fetch(self, url, mode, options):
        kw = dict(timeout=options.timeout, proxy=options.proxy,
                  cookies=options.cookies or None, extra_headers=options.extra_headers or None)
        if mode == "fast":
            return await self._fast.fetch(url, impersonate=options.impersonate, **kw)
        elif mode == "browser":
            return await self._browser.fetch(url, wait_for_selector=options.wait_for_selector,
                                              screenshot=options.screenshot, **kw)
        else:
            return await self._aggressive.fetch(url, wait_for_selector=options.wait_for_selector,
                                                screenshot=options.screenshot, **kw)


def _extract_domain(url):
    try:
        return urlparse(url).netloc.lower().split(":")[0]
    except Exception:
        return url


_orchestrator: Orchestrator | None = None

def get_orchestrator() -> Orchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator
