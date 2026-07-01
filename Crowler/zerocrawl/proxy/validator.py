"""Proxy health checker."""
from __future__ import annotations
import asyncio
import time
from typing import Optional

TEST_URL = "http://httpbin.org/ip"

async def validate_proxy(proxy_url: str, timeout: int = 10) -> dict:
    """Test a proxy for connectivity. Returns {valid, latency_ms, ip}."""
    t0 = time.time()
    try:
        import curl_cffi.requests as curl_req
        loop = asyncio.get_event_loop()
        resp = await loop.run_in_executor(
            None,
            lambda: curl_req.get(TEST_URL, proxies={"http": proxy_url, "https": proxy_url}, timeout=timeout)
        )
        latency_ms = int((time.time() - t0) * 1000)
        if resp.status_code == 200:
            try:
                ip = resp.json().get("origin", "unknown")
            except Exception:
                ip = "unknown"
            return {"valid": True, "latency_ms": latency_ms, "ip": ip}
    except Exception:
        pass
    return {"valid": False, "latency_ms": int((time.time()-t0)*1000), "ip": None}
