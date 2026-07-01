import pytest
from zerocrawl.extraction.links import classify_links

HTML_LINKS = """<html><body>
<a href="/about">About</a>
<a href="?page=3">Page 3</a>
<a href="https://external.com">External</a>
<a href="/docs/guide.pdf">Download</a>
</body></html>"""
BASE_URL = "https://example.com"

def test_internal_links():
    data = classify_links(HTML_LINKS, BASE_URL)
    assert any("/about" in u for u in data["internal"])

def test_external_links():
    data = classify_links(HTML_LINKS, BASE_URL)
    assert any("external.com" in u for u in data["external"])

def test_pagination():
    data = classify_links(HTML_LINKS, BASE_URL)
    assert len(data["pagination"]) >= 1

def test_downloads():
    data = classify_links(HTML_LINKS, BASE_URL)
    assert any(".pdf" in u for u in data["downloads"])
