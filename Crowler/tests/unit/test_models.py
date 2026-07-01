import pytest
from zerocrawl.models import ScrapeOptions, ScrapeResult, ContentBlock, MetadataBlock

def test_scrape_options_defaults():
    opts = ScrapeOptions()
    assert opts.mode == "auto"
    assert opts.timeout == 60
    assert opts.cache_ttl == 3600
    assert opts.respect_robots_txt is True

def test_scrape_options_mode():
    opts = ScrapeOptions(mode="browser")
    assert opts.mode == "browser"

def test_scrape_result_defaults():
    r = ScrapeResult(url="https://example.com")
    assert r.status == "success"
    assert r.content.markdown == ""
    assert r.ai_extracted is None

def test_scrape_result_serialization():
    r = ScrapeResult(url="https://example.com", status="success",
                     content=ContentBlock(markdown="# Hello", text="Hello", word_count=1, char_count=5))
    d = r.to_dict()
    assert d["url"] == "https://example.com"
    assert d["content"]["markdown"] == "# Hello"
    j = r.to_json()
    assert "example.com" in j
