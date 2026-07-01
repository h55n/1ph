import pytest
from zerocrawl.extraction.metadata import extract_metadata

HTML_FULL = """<html lang="en">
<head>
  <title>Product Page | Shop</title>
  <meta name="description" content="Buy the best product here.">
  <meta name="author" content="John Doe">
  <meta name="keywords" content="product, buy, shop">
  <link rel="canonical" href="https://example.com/product">
  <link rel="icon" href="/favicon.ico">
  <meta property="og:title" content="OG Product Title">
  <meta property="og:site_name" content="MyShop">
  <meta property="article:published_time" content="2024-01-15T10:00:00Z">
</head>
<body><h1>Product</h1></body></html>"""

def test_extracts_title():
    meta = extract_metadata(HTML_FULL)
    assert meta["title"] == "Product Page | Shop"

def test_extracts_description():
    meta = extract_metadata(HTML_FULL)
    assert meta["description"] == "Buy the best product here."

def test_extracts_author():
    meta = extract_metadata(HTML_FULL)
    assert meta["author"] == "John Doe"

def test_extracts_keywords():
    meta = extract_metadata(HTML_FULL)
    assert "product" in meta["keywords"]

def test_extracts_language():
    meta = extract_metadata(HTML_FULL)
    assert meta["language"] == "en"

def test_extracts_og():
    meta = extract_metadata(HTML_FULL)
    assert meta["open_graph"].get("title") == "OG Product Title"
    assert meta["site_name"] == "MyShop"

def test_extracts_published_date():
    meta = extract_metadata(HTML_FULL)
    assert meta["published_date"] == "2024-01-15"

def test_empty_html():
    meta = extract_metadata("")
    assert meta["title"] is None
