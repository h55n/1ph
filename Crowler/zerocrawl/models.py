"""
ZeroCrawl — Data Models
All Pydantic v2 models defining inputs, outputs, and configuration.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field, field_validator


# ──────────────────────────────────────────────────────────────────────────────
# Input / Configuration Models
# ──────────────────────────────────────────────────────────────────────────────

class ScrapeOptions(BaseModel):
    """Options for a single scrape request."""
    formats: list[Literal["markdown", "html", "text", "structured"]] = Field(
        default=["markdown", "structured"],
        description="Which output formats to include in the result.",
    )
    mode: Literal["auto", "fast", "browser", "aggressive"] = Field(
        default="auto",
        description="Fetch mode. auto = try fast first, fall back as needed.",
    )
    screenshot: bool = Field(default=False)
    wait_for_selector: Optional[str] = Field(
        default=None,
        description="CSS selector to wait for before extracting (browser modes only).",
    )
    timeout: int = Field(default=60, ge=5, le=300)
    cache_ttl: int = Field(
        default=3600,
        description="Seconds to cache this result. 0 = no cache.",
    )
    force_refresh: bool = Field(default=False)
    proxy: Optional[str] = Field(default=None, description="Proxy URL, e.g. http://host:port")
    cookies: dict[str, str] = Field(default_factory=dict)
    extra_headers: dict[str, str] = Field(default_factory=dict)
    respect_robots_txt: bool = Field(default=True)
    impersonate: Literal[
        "chrome120", "chrome119", "chrome118", "chrome116",
        "firefox121", "firefox120", "safari17", "safari16", "edge120"
    ] = Field(default="chrome120")


class CrawlOptions(BaseModel):
    """Options for a full-site crawl."""
    start_url: str
    max_depth: int = Field(default=3, ge=1, le=20)
    max_pages: int = Field(default=100, ge=1, le=10000)
    concurrency: int = Field(default=3, ge=1, le=20)
    same_domain: bool = Field(default=True)
    same_subdomain: bool = Field(default=False)
    include_patterns: list[str] = Field(default_factory=list)
    exclude_patterns: list[str] = Field(
        default=["*/tag/*", "*/author/*", "*/feed/*", "*/rss/*", "*.xml"],
    )
    scrape_options: ScrapeOptions = Field(default_factory=ScrapeOptions)


class ProxyConfig(BaseModel):
    """Proxy configuration."""
    strategy: Literal["own_ip", "free_pool", "tor", "custom"] = Field(default="own_ip")
    custom_proxy: Optional[str] = None
    rotate_every_n_requests: int = Field(default=50)
    validate_on_startup: bool = Field(default=True)
    tor_new_circuit_every: int = Field(default=10)


# ──────────────────────────────────────────────────────────────────────────────
# Output Models
# ──────────────────────────────────────────────────────────────────────────────

class ContentBlock(BaseModel):
    """Raw and formatted content extracted from the page."""
    markdown: str = ""
    html: str = ""
    text: str = ""
    word_count: int = 0
    char_count: int = 0


class MetadataBlock(BaseModel):
    """Metadata extracted from HTML head and meta tags."""
    title: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None
    published_date: Optional[str] = None   # ISO 8601
    modified_date: Optional[str] = None    # ISO 8601
    language: Optional[str] = None         # ISO 639-1
    keywords: list[str] = Field(default_factory=list)
    canonical_url: Optional[str] = None
    favicon_url: Optional[str] = None
    site_name: Optional[str] = None


class LinkBlock(BaseModel):
    """Classified links found on the page."""
    internal: list[str] = Field(default_factory=list)
    external: list[str] = Field(default_factory=list)
    pagination: list[str] = Field(default_factory=list)
    downloads: list[str] = Field(default_factory=list)


class ImageItem(BaseModel):
    """An image element with context."""
    src: str
    alt: str = ""
    context: str = ""
    width: Optional[int] = None
    height: Optional[int] = None


class PatternBlock(BaseModel):
    """Regex-detected data patterns."""
    emails: list[str] = Field(default_factory=list)
    phones: list[str] = Field(default_factory=list)
    prices: list[dict[str, Any]] = Field(default_factory=list)   # [{amount, currency}]
    dates: list[str] = Field(default_factory=list)               # ISO 8601
    urls: list[str] = Field(default_factory=list)
    social_handles: dict[str, str] = Field(default_factory=dict)


class StructuredBlock(BaseModel):
    """All rule-based structured data extracted from the page."""
    schema_org: list[dict[str, Any]] = Field(default_factory=list)
    open_graph: dict[str, str] = Field(default_factory=dict)
    twitter_card: dict[str, str] = Field(default_factory=dict)
    tables: list[list[dict[str, Any]]] = Field(default_factory=list)
    links: LinkBlock = Field(default_factory=LinkBlock)
    images: list[ImageItem] = Field(default_factory=list)
    patterns: PatternBlock = Field(default_factory=PatternBlock)


class ScrapeResult(BaseModel):
    """The complete result of a single scrape operation."""

    # Request info
    url: str
    final_url: str = ""
    status: Literal["success", "partial", "failed"] = "success"
    mode: Literal["fast", "browser", "aggressive", "unknown"] = "unknown"
    timing_ms: int = 0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # Content
    content: ContentBlock = Field(default_factory=ContentBlock)

    # Metadata
    metadata: MetadataBlock = Field(default_factory=MetadataBlock)

    # Structured data
    structured: StructuredBlock = Field(default_factory=StructuredBlock)

    # Optional AI extraction
    ai_extracted: Optional[dict[str, Any]] = None
    ai_error: Optional[str] = None

    # Error info
    error: Optional[str] = None
    error_type: Optional[str] = None  # "blocked", "timeout", "parse_error", "captcha"

    # Debug
    screenshot_b64: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")

    def to_json(self) -> str:
        return self.model_dump_json(indent=2)


# ──────────────────────────────────────────────────────────────────────────────
# Job / Queue Models
# ──────────────────────────────────────────────────────────────────────────────

class JobStatus(BaseModel):
    """Status of a batch or crawl job."""
    id: str
    type: Literal["scrape", "crawl", "batch", "map"]
    status: Literal["queued", "running", "completed", "failed", "cancelled"]
    total: int = 0
    completed: int = 0
    failed: int = 0
    skipped: int = 0
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    stats: dict[str, Any] = Field(default_factory=dict)

    @property
    def progress_pct(self) -> float:
        if self.total == 0:
            return 0.0
        return round((self.completed + self.failed) / self.total * 100, 1)


class BatchJob(BaseModel):
    """Reference to a submitted batch job."""
    id: str
    status: Literal["queued", "running", "completed", "failed", "cancelled"] = "queued"
    urls: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    async def get_status(self) -> "JobStatus":
        """Convenience: fetch current status from the queue manager."""
        from zerocrawl.queue.manager import JobManager
        return await JobManager.get_status(self.id)

    async def get_results(self) -> list[ScrapeResult]:
        """Convenience: fetch all completed results."""
        from zerocrawl.queue.manager import JobManager
        return await JobManager.get_results(self.id)
