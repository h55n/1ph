import pytest
from zerocrawl.extraction.structured import extract_schema_org, extract_open_graph, extract_twitter_card

HTML_SCHEMA = """<html><head>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Product","name":"Awesome Widget","offers":{"@type":"Offer","price":"29.99","priceCurrency":"USD"}}
</script>
<meta property="og:title" content="Awesome Widget">
<meta name="twitter:card" content="summary">
</head><body></body></html>"""

def test_extract_schema_org_product():
    results = extract_schema_org(HTML_SCHEMA)
    assert len(results) == 1
    assert results[0]["@type"] == "Product"
    assert results[0]["name"] == "Awesome Widget"

def test_extract_open_graph():
    og = extract_open_graph(HTML_SCHEMA)
    assert og.get("title") == "Awesome Widget"

def test_extract_twitter_card():
    tc = extract_twitter_card(HTML_SCHEMA)
    assert tc.get("card") == "summary"

def test_empty_html():
    assert extract_schema_org("") == []
    assert extract_open_graph("") == {}
