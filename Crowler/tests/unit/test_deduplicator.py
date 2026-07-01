import pytest
from zerocrawl.crawl.deduplicator import Deduplicator, fingerprint, normalise_url

def test_dedup_basic():
    d = Deduplicator()
    assert d.check_and_mark("https://example.com/page") is True
    assert d.check_and_mark("https://example.com/page") is False

def test_dedup_different_urls():
    d = Deduplicator()
    assert d.check_and_mark("https://a.com") is True
    assert d.check_and_mark("https://b.com") is True

def test_fingerprint_normalises_fragment():
    fp1 = fingerprint("https://example.com/page#section1")
    fp2 = fingerprint("https://example.com/page#section2")
    assert fp1 == fp2  # fragments stripped

def test_fingerprint_normalises_query_order():
    fp1 = fingerprint("https://example.com/page?a=1&b=2")
    fp2 = fingerprint("https://example.com/page?b=2&a=1")
    assert fp1 == fp2

def test_dedup_count():
    d = Deduplicator()
    d.check_and_mark("https://a.com")
    d.check_and_mark("https://b.com")
    d.check_and_mark("https://a.com")
    assert d.count() == 2
