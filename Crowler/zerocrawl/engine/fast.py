"""
ZeroCrawl — Mode 1: Fast Path
curl_cffi with TLS fingerprint mimicry. No browser launched.
~2–10s avg. Handles ~65% of the public web.
"""
from __future__ import annotations

import time
from typing import Any, Optional

from loguru import logger

from ..anti_detection.fingerprint import get_curl_cffi_target
from ..anti_detection.headers import get_headers


class FastFetcher:
    """
    Fetches pages using curl_cffi — a real browser TLS fingerprint with no browser.
    """

    def __init__(self) -> None:
        try:
            import curl_cffi.requests as curl_requests
            self._curl = curl_requests
            self._available = True
        except ImportError:
            logger.warning("curl_cffi not installed — Mode 1 unavailable. Run: pip install curl-cffi")
            self._curl = None
            self._available = False

    async def fetch(
        self,
        url: str,
        impersonate: str = "chrome120",
        timeout: int = 30,
        proxy: Optional[str] = None,
        cookies: Optional[dict] = None,
        extra_headers: Optional[dict] = None,
    ) -> dict[str, Any]:
        """
        Fetch a URL using TLS-mimicking curl_cffi.

        Returns:
            {
              "html": str,
              "status_code": int,
              "final_url": str,
              "headers": dict,
              "timing_ms": int,
              "error": str | None,
            }
        """
        if not self._available:
            return {
                "html": "",
                "status_code": 0,
                "final_url": url,
                "headers": {},
                "timing_ms": 0,
                "error": "curl_cffi not available",
            }

        curl_target = get_curl_cffi_target(impersonate)
        headers = get_headers(impersonate)
        if extra_headers:
            headers.update(extra_headers)

        t0 = time.time()
        try:
            import asyncio
            # curl_cffi is synchronous — run in executor to not block event loop
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self._curl.get(
                    url,
                    headers=headers,
                    impersonate=curl_target,
                    timeout=timeout,
                    allow_redirects=True,
                    proxies={"http": proxy, "https": proxy} if proxy else None,
                    cookies=cookies or {},
                ),
            )
            timing_ms = int((time.time() - t0) * 1000)

            # Decode response
            try:
                html = response.text
            except Exception:
                html = response.content.decode("utf-8", errors="replace")

            return {
                "html": html,
                "status_code": response.status_code,
                "final_url": str(response.url),
                "headers": dict(response.headers),
                "timing_ms": timing_ms,
                "error": None,
            }

        except Exception as e:
            timing_ms = int((time.time() - t0) * 1000)
            logger.debug(f"Mode 1 fetch failed for {url}: {e}")
            return {
                "html": "",
                "status_code": 0,
                "final_url": url,
                "headers": {},
                "timing_ms": timing_ms,
                "error": str(e),
            }


# Module-level singleton
_fetcher: FastFetcher | None = None


def get_fast_fetcher() -> FastFetcher:
    global _fetcher
    if _fetcher is None:
        _fetcher = FastFetcher()
    return _fetcher
