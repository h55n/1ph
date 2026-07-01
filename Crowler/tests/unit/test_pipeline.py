import pytest
from zerocrawl.extraction.pipeline import run_pipeline

ARTICLE_HTML = """<html lang="en">
<head>
  <title>How to Build a Scraper | Tech Blog</title>
  <meta name="description" content="Learn to build a scraper step by step.">
  <meta name="author" content="Jane Developer">
  <script type="application/ld+json">
  {"@context":"https://schema.org","@type":"Article","headline":"How to Build a Scraper","author":{"@type":"Person","name":"Jane Developer"}}
  </script>
</head>
<body>
  <article>
    <h1>How to Build a Scraper</h1>
    <p>Web scraping is the process of automatically extracting data from websites.</p>
    <p>There are many approaches: HTTP requests, headless browsers, or dedicated libraries.</p>
    <p>Contact the author at jane@example.com for questions.</p>
    <p>The price of the premium course is $99.99.</p>
    <table>
      <thead><tr><th>Tool</th><th>Speed</th></tr></thead>
      <tbody>
        <tr><td>requests</td><td>Fast</td></tr>
        <tr><td>playwright</td><td>Slow</td></tr>
      </tbody>
    </table>
  </article>
</body></html>"""

def test_pipeline_returns_result():
    result = run_pipeline(ARTICLE_HTML, url="https://example.com/article")
    assert result is not None
    assert result.url == "https://example.com/article"

def test_pipeline_extracts_title():
    result = run_pipeline(ARTICLE_HTML, url="https://example.com/article")
    assert result.metadata.title is not None
    assert "Scraper" in result.metadata.title

def test_pipeline_extracts_content():
    result = run_pipeline(ARTICLE_HTML, url="https://example.com/article")
    assert result.content.word_count > 0
    assert len(result.content.markdown) > 0

def test_pipeline_extracts_schema_org():
    result = run_pipeline(ARTICLE_HTML, url="https://example.com/article")
    assert len(result.structured.schema_org) >= 1
    assert result.structured.schema_org[0]["@type"] == "Article"

def test_pipeline_extracts_email():
    result = run_pipeline(ARTICLE_HTML, url="https://example.com/article")
    assert "jane@example.com" in result.structured.patterns.emails

def test_pipeline_extracts_price():
    result = run_pipeline(ARTICLE_HTML, url="https://example.com/article")
    prices = result.structured.patterns.prices
    assert len(prices) >= 1
    assert any(p["amount"] == 99.99 for p in prices)

def test_pipeline_extracts_table():
    result = run_pipeline(ARTICLE_HTML, url="https://example.com/article")
    assert len(result.structured.tables) >= 1
    table = result.structured.tables[0]
    tools = [row.get("Tool", "") for row in table]
    assert "requests" in tools

def test_pipeline_empty_html():
    result = run_pipeline("", url="https://example.com")
    assert result.status == "failed"
    assert result.error is not None
