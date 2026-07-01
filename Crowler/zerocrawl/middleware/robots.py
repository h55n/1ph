"""Robots.txt enforcement middleware."""
from __future__ import annotations
from typing import Any
from .base import BaseMiddleware
from ..anti_detection.robots import is_allowed

class RobotsMiddleware(BaseMiddleware):
    async def process_request(self, request: dict[str, Any]) -> dict[str, Any]:
        url = request.get("url", "")
        if request.get("respect_robots_txt", True) and url:
            if not is_allowed(url):
                raise PermissionError(f"Disallowed by robots.txt: {url}")
        return request

    async def process_response(self, request: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
        return response
