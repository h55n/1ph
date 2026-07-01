"""
ZeroCrawl — Mode 3: Aggressive Path
Browser + Camoufox + Human Behavior Simulation.
"""
from __future__ import annotations

import asyncio
import base64
import random
import time
from typing import Any, Optional

from loguru import logger

from .browser import BrowserFetcher


def _bezier_points(start, end, steps=20):
    cp_x = (start[0] + end[0]) / 2 + random.uniform(-100, 100)
    cp_y = (start[1] + end[1]) / 2 + random.uniform(-100, 100)
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = (1-t)**2 * start[0] + 2*(1-t)*t*cp_x + t**2 * end[0]
        y = (1-t)**2 * start[1] + 2*(1-t)*t*cp_y + t**2 * end[1]
        pts.append((x, y))
    return pts


class AggressiveFetcher:
    def __init__(self):
        self._browser_fetcher = BrowserFetcher()

    async def fetch(self, url, timeout=120, proxy=None, cookies=None,
                    wait_for_selector=None, screenshot=False, extra_headers=None):
        t0 = time.time()
        try:
            pool = await self._browser_fetcher._get_pool()
            context = await pool.get_context()
            if context is None:
                raise RuntimeError("No browser context available")
            return await self._aggressive_fetch(
                context, url, timeout, proxy, cookies,
                wait_for_selector, screenshot, extra_headers, t0
            )
        except Exception as e:
            timing_ms = int((time.time() - t0) * 1000)
            logger.debug(f"Mode 3 failed for {url}: {e}")
            return {"html": "", "status_code": 0, "final_url": url,
                    "headers": {}, "timing_ms": timing_ms, "error": str(e),
                    "screenshot_b64": None}

    async def _aggressive_fetch(self, context, url, timeout, proxy, cookies,
                                 wait_for_selector, screenshot, extra_headers, t0):
        from urllib.parse import urlparse
        page = None
        try:
            page = await context.new_page()
            if extra_headers:
                await page.set_extra_http_headers(extra_headers)
            if cookies:
                await context.add_cookies([
                    {"name": k, "value": v, "url": url} for k, v in cookies.items()
                ])

            # Navigate homepage first for realistic referrer
            parsed = urlparse(url)
            homepage = f"{parsed.scheme}://{parsed.netloc}"
            if homepage.rstrip("/") != url.rstrip("/"):
                try:
                    await page.goto(homepage, wait_until="domcontentloaded", timeout=20_000)
                    await asyncio.sleep(max(0.5, random.gauss(2.0, 0.8)))
                    await self._scroll(page)
                    await asyncio.sleep(max(0.3, random.gauss(1.5, 0.5)))
                except Exception:
                    pass

            response = await page.goto(url, wait_until="networkidle", timeout=timeout * 1000)
            await asyncio.sleep(max(0.5, random.gauss(2.0, 0.8)))
            await self._scroll(page)
            await self._mouse_move(page)

            if wait_for_selector:
                try:
                    await page.wait_for_selector(wait_for_selector, timeout=15_000)
                except Exception:
                    pass

            await asyncio.sleep(max(0.3, random.gauss(1.5, 0.5)))

            html = await page.content()
            final_url = page.url
            status_code = response.status if response else 200

            screenshot_b64 = None
            if screenshot:
                try:
                    screenshot_b64 = base64.b64encode(
                        await page.screenshot(full_page=True)
                    ).decode()
                except Exception:
                    pass

            return {"html": html, "status_code": status_code, "final_url": final_url,
                    "headers": {}, "timing_ms": int((time.time()-t0)*1000),
                    "error": None, "screenshot_b64": screenshot_b64}
        finally:
            if page:
                try:
                    await page.close()
                except Exception:
                    pass

    async def _scroll(self, page):
        try:
            height = await page.evaluate("document.body.scrollHeight")
            steps = random.randint(4, 6)
            for i in range(1, steps + 1):
                await page.evaluate(f"window.scrollTo(0, {(height*i)//steps})")
                await asyncio.sleep(random.uniform(0.4, 1.8))
            await page.evaluate(f"window.scrollTo(0, {int(height*0.7)})")
        except Exception:
            pass

    async def _mouse_move(self, page):
        try:
            v = page.viewport_size or {"width": 1280, "height": 800}
            w, h = v.get("width", 1280), v.get("height", 800)
            pos = (random.uniform(0, w), random.uniform(0, h))
            for _ in range(random.randint(2, 4)):
                target = (random.uniform(50, w-50), random.uniform(50, h-50))
                for pt in _bezier_points(pos, target, steps=15):
                    await page.mouse.move(pt[0], pt[1])
                    await asyncio.sleep(random.uniform(0.01, 0.04))
                pos = target
                await asyncio.sleep(random.uniform(0.2, 0.8))
        except Exception:
            pass
