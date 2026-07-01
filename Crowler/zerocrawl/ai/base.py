"""Abstract base class for AI extractors."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Optional

class AIExtractor(ABC):
    @abstractmethod
    async def extract(self, content: str, schema: dict[str, Any], context: str = "") -> dict[str, Any]:
        """
        Extract structured data from markdown content per schema.
        Returns dict matching schema keys. Raises on hard failure.
        """
        raise NotImplementedError
