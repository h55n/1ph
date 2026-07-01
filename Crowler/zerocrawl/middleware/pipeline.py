"""Middleware pipeline orchestrator."""
from __future__ import annotations
from typing import Any, Callable, Awaitable, Optional
from .base import BaseMiddleware

class MiddlewarePipeline:
    def __init__(self) -> None:
        self._middlewares: list[BaseMiddleware] = []

    def add(self, middleware: BaseMiddleware) -> "MiddlewarePipeline":
        self._middlewares.append(middleware)
        return self

    async def process_request(self, request: dict[str, Any]) -> dict[str, Any]:
        for mw in self._middlewares:
            request = await mw.process_request(request)
        return request

    async def process_response(self, request: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
        for mw in reversed(self._middlewares):
            response = await mw.process_response(request, response)
        return response
