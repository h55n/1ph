"""Base middleware abstract class."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Callable, Awaitable

class BaseMiddleware(ABC):
    @abstractmethod
    async def process_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Called before the request is made. Modify request dict in place."""
        return request

    @abstractmethod
    async def process_response(self, request: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
        """Called after the response is received. Can modify or raise."""
        return response
