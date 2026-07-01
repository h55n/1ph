"""
ZeroCrawl — Mode 2: Browser Path
Playwright + Camoufox hardened Firefox. JS-rendered content. Browser pool.
~15–60s avg. Handles ~90% of the public web.
"""
from __future__ import annotations

import asyncio
import base64
import random
import time
from typing import Any, Optional

from loguru import logger

from ..anti_detection.session import FingerprintProfile, SessionPool, generate_fingerprint_profile
from ..config import settings


class BrowserPool:
    """
    Manages a pool of Camoufox/Playwright browser contexts.
    Each context has a unique fingerprint profile.
    Contexts are reused across requests; retired after max_requests.
    """

    def __init__(self, pool_size: int = 1) -> None:
        self.pool_size = pool_size
        self._session_pool = SessionPool(pool_size=pool_size)
        self._playwright = None
        self._pw_cm = None
        self._browsers: list[Any] = []
        self._contexts: list[Any] = []
        self._lock = asyncio.Lock()
        self._ready = False
        self._use_camoufox = False

    async def start(self) -> None:
        if self._ready:
            return
        async with self._lock:
            if self._ready:
                return
            try:
                await self._launch_browsers()
                self._ready = True
                logger.info(f"Browser pool ready with {self.pool_size} instance(s)")
            except Exception as e:
                logger.error(f"Failed to start browser pool: {e}")
                raise

    async def _launch_browsers(self) -> None:
        try:
            import camoufox  # noqa: F401
            self._use_camoufox = True
        except ImportError:
            self._use_camoufox = False
            logger.warning("Camoufox not available — using plain Playwright Firefox")

        try:
            from playwright.async_api import async_playwright
            self._pw_cm = async_playwright()
            self._playwright = await self._pw_cm.__aenter__()
        except ImportError:
            raise RuntimeError("playwright not installed. Run: playwright install firefox")

        for _ in range(self.pool_size):
            profile = generate_fingerprint_profile()
            context = await self._launch_context(profile)
            self._browsers.append(profile)
            self._contexts.append(context)

    async def _launch_context(self, profile: FingerprintProfile) -> Any:
        if self._use_camoufox:
            try:
                from camoufox.async_api import AsyncCamoufox
                camoufox_cm = AsyncCamoufox(
                    headless=settings.browser_headless,
                    screen={"width": profile.screen_width, "height": profile.screen_height},
                    locale=profile.locale,
                    timezone=profile.timezone,
                )
                browser = await camoufox_cm.__aenter__()
                context = await browser.new_context(
                    locale=profile.locale,
                    timezone_id=profile.timezone,
                    viewport={"width": profile.screen_width, "height": profile.screen_height},
                )
                return context
            except Exception as e:
                logger.warning(f"Camoufox launch failed ({e}), falling back to plain Firefox")

        # Plain playwright Firefox
        browser = await self._playwright.firefox.launch(
            headless=settings.browser_headless,
        )
        context = await browser.new_context(
            locale=profile.locale,
            timezone_id=profile.timezone,
            viewport={"width": profile.screen_width, "height": profile.screen_height},
            user_agent=profile.user_agent,
        )
        return context

    async def get_context(self) -> Any:
        if not self._ready:
            await self.start()
        return self._contexts[0] if self._contexts else None

    async def stop(self) -> None:
        for context in self._contexts:
            try:
                await context.close()
            except Exception:
                pass
        self._browsers.clear()
        self._contexts.clear()
        self._ready = False
        if self._pw_cm and self._playwright:
            try:
                await self._pw_cm.__aexit__(None, None, None)
            except Exception:
                pass


class BrowserFetcher:
    def __init__(self, pool: Optional[BrowserPool] = None) -> None:
        self._pool = pool

    async def _get_pool(self) -> BrowserPool:
        if self._pool is None:
            self._pool = _get_global_pool()
        if not self._pool._ready:
            await self._pool.start()
        return self._pool

    async def fetch(
        self,
        url: str,
        timeout: int = 60,
        proxy: Optional[str] = None,
        cookies: Optional[dict] = None,
        wait_for_selector: Optional[str] = None,
        screenshot: bool = False,
        extra_headers: Optional[dict] = None,
    ) -> dict[str, Any]:
        t0 = time.time()
        try:
            pool = await self._get_pool()
            context = await pool.get_context()
            if context is None:
                raise RuntimeError("No browser context available")
            return await self._do_fetch(
                context=context, url=url, timeout=timeout, proxy=proxy,
                cookies=cookies, wait_for_selector=wait_for_selector,
                screenshot=screenshot, extra_headers=extra_headers, t0=t0,
            )
        except Exception as e:
            timing_ms = int((time.time() - t0) * 1000)
            logger.debug(f"Mode 2 fetch failed for {url}: {e}")
            return {
                "html": "", "status_code": 0, "final_url": url,
                "headers": {}, "timing_ms": timing_ms, "error": str(e),
                "screenshot_b64": None,
            }

    async def _do_fetch(
        self, context: Any, url: str, timeout: int, proxy: Optional[str],
        cookies: Optional[dict], wait_for_selector: Optional[str],
        screenshot: bool, extra_headers: Optional[dict], t0: float,
    ) -> dict[str, Any]:
        page = None
        try:
            page = await context.new_page()
            timeout_ms = timeout * 1000

            if extra_headers:
                await page.set_extra_http_headers(extra_headers)
            if cookies:
                await context.add_cookies([
                    {"name": k, "value": v, "url": url} for k, v in cookies.items()
                ])

            response = await page.goto(url, wait_until="networkidle", timeout=timeout_ms)

            if wait_for_selector:
                try:
                    await page.wait_for_selector(wait_for_selector, timeout=15_000)
                except Exception:
                    pass

            await asyncio.sleep(random.uniform(1.0, 2.5))

            html = await page.content()
            final_url = page.url
            status_code = response.status if response else 200

            screenshot_b64 = None
            if screenshot:
                try:
                    png_bytes = await page.screenshot(full_page=True)
                    screenshot_b64 = base64.b64encode(png_bytes).decode()
                except Exception:
                    pass

            timing_ms = int((time.time() - t0) * 1000)
            return {
                "html": html, "status_code": status_code, "final_url": final_url,
                "headers": {}, "timing_ms": timing_ms, "error": None,
                "screenshot_b64": screenshot_b64,
            }
        finally:
            if page:
                try:
                    await page.close()
                except Exception:
                    pass


_global_pool: BrowserPool | None = None


def _get_global_pool() -> BrowserPool:
    global _global_pool
    if _global_pool is None:
        size = settings.auto_browser_pool_size()
        _global_pool = BrowserPool(pool_size=size)
    return _global_pool


async def stop_browser_pool() -> None:
    global _global_pool
    if _global_pool and _global_pool._ready:
        await _global_pool.stop()
        _global_pool = None
