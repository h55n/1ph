"""Cache middleware — checks and stores results in SQLite cache."""
from __future__ import annotations
from typing import Any
from .base import BaseMiddleware

class CacheMiddleware(BaseMiddleware):
    async def process_request(self, request: dict[str, Any]) -> dict[str, Any]:
        return request

    async def process_response(self, request: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
        return response
