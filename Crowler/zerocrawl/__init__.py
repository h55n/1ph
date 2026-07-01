"""
ZeroCrawl — Zero-cost, plug-and-play web scraping engine.

Quick start:
    import asyncio
    from zerocrawl import scrape

    result = asyncio.run(scrape("https://example.com"))
    print(result.content.markdown)

Or synchronously:
    from zerocrawl import scrape_sync
    result = scrape_sync("https://example.com")
"""
from __future__ import annotations

import asyncio
from typing import AsyncIterator, Optional

from .models import (
    BatchJob,
    CrawlOptions,
    JobStatus,
    ScrapeOptions,
    ScrapeResult,
)

__version__ = "1.0.0"
__all__ = [
    "scrape",
    "scrape_sync",
    "crawl",
    "map_urls",
    "batch_scrape",
    "ScrapeOptions",
    "CrawlOptions",
    "ScrapeResult",
    "BatchJob",
    "JobStatus",
]


async def scrape(
    url: str,
    options: Optional[ScrapeOptions] = None,
    ai_extractor=None,
    ai_schema: Optional[dict] = None,
    cache_ttl: int = 3600,
    force_refresh: bool = False,
    mode: str = "auto",
    timeout: int = 60,
    screenshot: bool = False,
    proxy: Optional[str] = None,
) -> ScrapeResult:
    """
    Scrape a single URL. The simplest possible usage:

        result = await scrape("https://example.com")
        print(result.content.markdown)

    Args:
        url: URL to scrape.
        options: Full ScrapeOptions object (overrides individual kwargs if provided).
        ai_extractor: Optional AIExtractor instance for AI-powered extraction.
        ai_schema: Schema dict for AI extraction (e.g. {"title": "string", "price": "number"}).
        cache_ttl: Seconds to cache the result (0 = no cache).
        force_refresh: Bypass the cache.
        mode: "auto" | "fast" | "browser" | "aggressive".
        timeout: Request timeout in seconds.
        screenshot: Whether to capture a screenshot (browser modes only).
        proxy: Optional proxy URL.

    Returns:
        ScrapeResult with content.markdown, metadata, structured data, etc.
    """
    from .engine.orchestrator import get_orchestrator
    from .queue.cache import get_cached, set_cached

    if options is None:
        options = ScrapeOptions(
            mode=mode,  # type: ignore
            timeout=timeout,
            cache_ttl=cache_ttl,
            force_refresh=force_refresh,
            screenshot=screenshot,
            proxy=proxy,
        )

    # Cache check
    if not options.force_refresh:
        cached = await get_cached(url, options.cache_ttl)
        if cached:
            return cached

    orchestrator = get_orchestrator()
    result = await orchestrator.scrape(url, options)

    # AI extraction (optional plugin)
    if ai_extractor is not None and ai_schema and result.content.markdown:
        try:
            result.ai_extracted = await ai_extractor.extract(
                result.content.markdown,
                ai_schema,
            )
        except Exception as e:
            result.ai_error = str(e)

    # Cache result
    if result.status != "failed" and options.cache_ttl > 0:
        await set_cached(url, result, options.cache_ttl)

    return result


def scrape_sync(
    url: str,
    options: Optional[ScrapeOptions] = None,
    **kwargs,
) -> ScrapeResult:
    """
    Synchronous wrapper around scrape() for use in non-async code.

        from zerocrawl import scrape_sync
        result = scrape_sync("https://example.com")
    """
    return asyncio.run(scrape(url, options, **kwargs))


async def map_urls(
    url: str,
    include_sitemap: bool = True,
) -> list[str]:
    """
    Discover all URLs under a domain without scraping their content.

        urls = await map_urls("https://example.com")
        print(f"Found {len(urls)} URLs")
    """
    from .crawl.sitemap import fetch_sitemap_urls
    from .extraction.links import classify_links

    if include_sitemap:
        urls = await fetch_sitemap_urls(url)
        if urls:
            return list(dict.fromkeys(urls))

    # Fallback: scrape homepage and extract links
    result = await scrape(url, ScrapeOptions(mode="fast", cache_ttl=3600))
    link_data = classify_links(result.content.html, url)
    return list(dict.fromkeys(link_data.get("internal", [])))


async def crawl(
    url: str,
    options: Optional[CrawlOptions] = None,
    max_pages: int = 100,
    max_depth: int = 3,
    concurrency: int = 3,
) -> AsyncIterator[ScrapeResult]:
    """
    Recursively scrape an entire site starting from a URL.

        async for result in crawl("https://example.com", max_pages=50):
            print(result.url, result.content.word_count)

    Yields ScrapeResult for each page as it completes.
    """
    from .crawl.crawler import SiteCrawler

    if options is None:
        options = CrawlOptions(
            start_url=url,
            max_pages=max_pages,
            max_depth=max_depth,
            concurrency=concurrency,
        )

    crawler = SiteCrawler(options)
    async for result in crawler.crawl():
        yield result


async def batch_scrape(
    urls: list[str],
    options: Optional[ScrapeOptions] = None,
    concurrency: int = 3,
    webhook_url: Optional[str] = None,
    webhook_secret: Optional[str] = None,
) -> BatchJob:
    """
    Submit multiple URLs as a batch job. Returns immediately with a job ID.

        job = await batch_scrape(["https://a.com", "https://b.com"])
        print(job.id)  # poll with job.get_status()
        results = await job.get_results()
    """
    import asyncio as _asyncio
    from .queue.manager import JobManager
    from .queue.worker import AsyncWorker

    if options is None:
        options = ScrapeOptions()

    job = await JobManager.create_batch_job(
        urls,
        webhook_url=webhook_url,
        webhook_secret=webhook_secret,
    )
    worker = AsyncWorker(job.id, options=options, concurrency=concurrency)
    _asyncio.create_task(worker.run())
    return job
