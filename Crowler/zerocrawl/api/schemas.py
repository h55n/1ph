"""FastAPI request/response schemas."""
from __future__ import annotations
from typing import Any, Literal, Optional
from pydantic import BaseModel

class ScrapeOptionsRequest(BaseModel):
    formats: list[str] = ["markdown", "structured"]
    mode: str = "auto"
    screenshot: bool = False
    wait_for_selector: Optional[str] = None
    timeout: int = 60
    cache_ttl: int = 3600
    force_refresh: bool = False
    proxy: Optional[str] = None
    cookies: dict[str, str] = {}
    extra_headers: dict[str, str] = {}
    respect_robots_txt: bool = True
    impersonate: str = "chrome120"

class AIRequest(BaseModel):
    provider: str = "ollama"
    model: Optional[str] = None
    schema_: Optional[dict[str, Any]] = None

class ScrapeRequest(BaseModel):
    url: str
    options: ScrapeOptionsRequest = ScrapeOptionsRequest()
    ai: Optional[AIRequest] = None

class BatchScrapeRequest(BaseModel):
    urls: list[str]
    options: ScrapeOptionsRequest = ScrapeOptionsRequest()
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None

class CrawlRequest(BaseModel):
    start_url: str
    max_depth: int = 3
    max_pages: int = 100
    concurrency: int = 3
    same_domain: bool = True
    include_patterns: list[str] = []
    exclude_patterns: list[str] = []

class MapRequest(BaseModel):
    url: str
    include_sitemap: bool = True
