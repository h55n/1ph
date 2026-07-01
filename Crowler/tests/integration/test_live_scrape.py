"""
Integration tests — require network access and real URLs.
Run with: pytest tests/integration/ -v
"""
import asyncio
import pytest
from zerocrawl import scrape
from zerocrawl.models import ScrapeOptions

pytestmark = pytest.mark.asyncio

@pytest.mark.asyncio
async def test_scrape_example_com():
    result = await scrape("https://example.com", options=ScrapeOptions(mode="fast", timeout=30, cache_ttl=0))
    assert result.status in ("success", "partial")
    assert result.metadata.title is not None
    assert "Example" in (result.metadata.title or "")
    assert result.content.word_count > 0

@pytest.mark.asyncio
async def test_scrape_returns_links():
    result = await scrape("https://example.com", options=ScrapeOptions(mode="fast", timeout=30, cache_ttl=0))
    assert isinstance(result.structured.links.external, list)

@pytest.mark.asyncio
async def test_scrape_httpbin():
    result = await scrape("https://httpbin.org/html", options=ScrapeOptions(mode="fast", timeout=30, cache_ttl=0))
    assert result.status in ("success", "partial")
    assert result.content.word_count > 0

@pytest.mark.asyncio
async def test_scrape_with_schema_org():
    result = await scrape("https://schema.org/Product", options=ScrapeOptions(mode="fast", timeout=30, cache_ttl=0))
    assert result.status in ("success", "partial")

@pytest.mark.asyncio
async def test_map_urls():
    from zerocrawl import map_urls
    urls = await map_urls("https://example.com")
    assert isinstance(urls, list)

@pytest.mark.asyncio
async def test_batch_scrape():
    from zerocrawl import batch_scrape
    job = await batch_scrape(["https://example.com", "https://httpbin.org/html"],
                              options=ScrapeOptions(mode="fast", timeout=30, cache_ttl=0), concurrency=2)
    assert job.id
    assert job.status == "queued"
    await asyncio.sleep(5)
    status = await job.get_status()
    assert status.total == 2
