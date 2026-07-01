import pytest
from zerocrawl.extraction.cleaner import html_to_markdown, extract_plain_text

HTML = """<html><body>
<h1>Main Title</h1>
<p>Paragraph with <strong>bold</strong> text.</p>
<ul><li>Item one</li><li>Item two</li></ul>
</body></html>"""

def test_html_to_markdown_heading():
    md = html_to_markdown(HTML)
    assert "Main Title" in md

def test_html_to_markdown_list():
    md = html_to_markdown(HTML)
    assert "Item one" in md

def test_extract_plain_text():
    text = extract_plain_text(HTML)
    assert "Main Title" in text
    assert "<" not in text

def test_empty_input():
    assert html_to_markdown("") == ""
    assert extract_plain_text("") == ""
