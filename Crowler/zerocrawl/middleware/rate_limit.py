"""Per-domain rate limiting middleware."""
from __future__ import annotations
from typing import Any
from ..anti_detection.timing import get_default_controller
from .base import BaseMiddleware
from urllib.parse import urlparse

class RateLimitMiddleware(BaseMiddleware):
    def __init__(self):
        self._controller = get_default_controller()

    async def process_request(self, request: dict[str, Any]) -> dict[str, Any]:
        url = request.get("url", "")
        domain = urlparse(url).netloc.lower().split(":")[0]
        # Timing is handled in orchestrator, so this is a no-op guard
        return request

    async def process_response(self, request: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
        return response
