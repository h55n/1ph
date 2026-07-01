"""Free proxy pool manager."""
from __future__ import annotations
import asyncio
import random
from typing import Optional
from loguru import logger
from .validator import validate_proxy

FREE_PROXY_SOURCES = [
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
]

class ProxyPool:
    def __init__(self):
        self._proxies: list[dict] = []
        self._idx = 0

    async def refresh(self, validate: bool = True) -> int:
        """Fetch and validate free proxies. Returns count of valid proxies."""
        raw = await self._fetch_proxy_list()
        if validate:
            results = await asyncio.gather(*[validate_proxy(f"http://{p}") for p in raw[:50]], return_exceptions=True)
            self._proxies = [
                {"url": f"http://{raw[i]}", "latency_ms": r["latency_ms"]}
                for i, r in enumerate(results)
                if isinstance(r, dict) and r.get("valid")
            ]
            logger.info(f"Proxy pool: {len(self._proxies)}/{len(raw[:50])} valid")
        else:
            self._proxies = [{"url": f"http://{p}", "latency_ms": 999} for p in raw]
        return len(self._proxies)

    async def _fetch_proxy_list(self) -> list[str]:
        import curl_cffi.requests as curl_req
        proxies = []
        for src in FREE_PROXY_SOURCES:
            try:
                import asyncio as _asyncio
                loop = _asyncio.get_event_loop()
                resp = await loop.run_in_executor(None, lambda: curl_req.get(src, timeout=10))
                if resp.status_code == 200:
                    for line in resp.text.strip().splitlines():
                        line = line.strip()
                        if ":" in line and not line.startswith("#"):
                            proxies.append(line)
            except Exception as e:
                logger.debug(f"Proxy source error {src}: {e}")
        return list(dict.fromkeys(proxies))

    def get_proxy(self) -> Optional[str]:
        if not self._proxies:
            return None
        proxy = self._proxies[self._idx % len(self._proxies)]
        self._idx += 1
        return proxy["url"]

    def retire_proxy(self, proxy_url: str) -> None:
        self._proxies = [p for p in self._proxies if p["url"] != proxy_url]

    def count(self) -> int:
        return len(self._proxies)
