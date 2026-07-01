import pytest
from zerocrawl.extraction.parser import pre_clean, extract_text, get_all_links, get_all_images

SAMPLE_HTML = """<html>
<head><title>Test Page</title></head>
<body>
  <main>
    <h1>Hello World</h1>
    <p>This is a test paragraph with some content.</p>
    <a href="https://external.com">External</a>
    <a href="/internal">Internal</a>
    <img src="/images/test.jpg" alt="Test image" width="800" height="600">
  </main>
  <script>var x = 1;</script>
  <style>body { color: red; }</style>
</body></html>"""

def test_pre_clean_removes_scripts():
    cleaned = pre_clean(SAMPLE_HTML)
    assert "<script>" not in cleaned
    assert "<style>" not in cleaned

def test_pre_clean_preserves_content():
    cleaned = pre_clean(SAMPLE_HTML)
    assert "Hello World" in cleaned

def test_extract_text():
    text = extract_text(SAMPLE_HTML)
    assert "Hello World" in text

def test_get_all_links():
    links = get_all_links(SAMPLE_HTML, "https://example.com")
    hrefs = [l["href"] for l in links]
    assert any("external.com" in h for h in hrefs)

def test_get_all_images():
    images = get_all_images(SAMPLE_HTML)
    assert len(images) >= 1
    assert images[0]["src"] == "/images/test.jpg"
    assert images[0]["alt"] == "Test image"
