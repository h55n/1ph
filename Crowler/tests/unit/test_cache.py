import asyncio
import pytest
from zerocrawl.models import ScrapeResult, ContentBlock
from zerocrawl.queue.cache import get_cached, set_cached, clear_cache, get_url_fingerprint

@pytest.fixture(autouse=True)
def clean():
    asyncio.get_event_loop().run_until_complete(clear_cache())
    yield
    asyncio.get_event_loop().run_until_complete(clear_cache())

def make_result(url):
    return ScrapeResult(url=url, final_url=url, status="success", mode="fast",
                        content=ContentBlock(markdown="# Hi", text="Hi", word_count=1, char_count=2))

@pytest.mark.asyncio
async def test_cache_miss():
    assert await get_cached("https://notcached.example.com") is None

@pytest.mark.asyncio
async def test_cache_set_get():
    url = "https://example.com/cache-test"
    await set_cached(url, make_result(url), ttl=3600)
    cached = await get_cached(url, ttl=3600)
    assert cached is not None
    assert cached.url == url

@pytest.mark.asyncio
async def test_cache_ttl_zero():
    url = "https://example.com/no-cache"
    await set_cached(url, make_result(url), ttl=0)
    assert await get_cached(url) is None

@pytest.mark.asyncio
async def test_cache_clear():
    url = "https://example.com/clear"
    await set_cached(url, make_result(url), ttl=3600)
    await clear_cache(url=url)
    assert await get_cached(url) is None

def test_fingerprint_stable():
    fp1 = get_url_fingerprint("https://example.com/page?b=2&a=1#hash")
    fp2 = get_url_fingerprint("https://example.com/page?b=2&a=1#hash")
    assert fp1 == fp2

def test_fingerprint_query_normalised():
    fp1 = get_url_fingerprint("https://example.com/page?a=1&b=2")
    fp2 = get_url_fingerprint("https://example.com/page?b=2&a=1")
    assert fp1 == fp2
