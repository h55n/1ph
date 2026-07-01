"""ZeroCrawl — Site Crawler."""
from __future__ import annotations
import asyncio
from typing import AsyncIterator
from loguru import logger
from ..models import CrawlOptions, ScrapeOptions, ScrapeResult
from ..engine.orchestrator import get_orchestrator
from ..extraction.links import classify_links
from .deduplicator import Deduplicator
from .scope import ScopeFilter
from .sitemap import fetch_sitemap_urls


class SiteCrawler:
    def __init__(self, options: CrawlOptions):
        self.options = options
        self._orchestrator = get_orchestrator()
        self._dedup = Deduplicator()
        self._scope = ScopeFilter(
            options.start_url,
            same_domain=options.same_domain,
            same_subdomain=options.same_subdomain,
            include_patterns=options.include_patterns,
            exclude_patterns=options.exclude_patterns,
        )

    async def crawl(self) -> AsyncIterator[ScrapeResult]:
        url_queue: list[tuple[str, int]] = [(self.options.start_url, 0)]
        self._dedup.mark_seen(self.options.start_url)
        scraped = 0

        # Pre-seed from sitemap
        try:
            sitemap_urls = await fetch_sitemap_urls(self.options.start_url)
            for url in sitemap_urls:
                if self._scope.is_in_scope(url) and self._dedup.check_and_mark(url):
                    url_queue.append((url, 1))
        except Exception as e:
            logger.debug(f"Sitemap error: {e}")

        semaphore = asyncio.Semaphore(self.options.concurrency)

        async def process_one(url: str, depth: int):
            async with semaphore:
                try:
                    result = await self._orchestrator.scrape(url, self.options.scrape_options)
                    new_links = []
                    if depth < self.options.max_depth and result.content.html:
                        link_data = classify_links(result.content.html, url)
                        for new_url in link_data.get("internal", []):
                            if (self._scope.is_in_scope(new_url)
                                    and self._dedup.check_and_mark(new_url)):
                                new_links.append(new_url)
                    return result, new_links
                except Exception as e:
                    logger.error(f"Crawl error for {url}: {e}")
                    return None, []

        while url_queue and scraped < self.options.max_pages:
            batch_size = min(self.options.concurrency, len(url_queue),
                             self.options.max_pages - scraped)
            batch = url_queue[:batch_size]
            url_queue = url_queue[batch_size:]

            tasks = [asyncio.create_task(process_one(url, depth)) for url, depth in batch]
            task_depths = {i: depth for i, (_, depth) in enumerate(batch)}

            for i, task in enumerate(tasks):
                result, new_links = await task
                if result:
                    scraped += 1
                    depth = task_depths[i]
                    for new_url in new_links:
                        if scraped + len(url_queue) < self.options.max_pages:
                            url_queue.append((new_url, depth + 1))
                    yield result
