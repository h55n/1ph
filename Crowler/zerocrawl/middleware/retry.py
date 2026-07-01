"""Retry middleware with exponential backoff."""
from __future__ import annotations
import asyncio
import random
from typing import Any
from loguru import logger
from .base import BaseMiddleware

class RetryMiddleware(BaseMiddleware):
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 30.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    async def process_request(self, request: dict[str, Any]) -> dict[str, Any]:
        request.setdefault("retry_count", 0)
        return request

    async def process_response(self, request: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
        status = response.get("status_code", 200)
        if status in (429, 503, 502) and request.get("retry_count", 0) < self.max_retries:
            retry = request["retry_count"] + 1
            delay = min(self.base_delay * (2 ** retry) + random.uniform(0, 1), self.max_delay)
            logger.debug(f"Retry {retry}/{self.max_retries} after {delay:.1f}s (HTTP {status})")
            await asyncio.sleep(delay)
            response["_retry"] = True
            response["_retry_count"] = retry
        return response
