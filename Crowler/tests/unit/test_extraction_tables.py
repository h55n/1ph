import pytest
from zerocrawl.extraction.tables import extract_tables

HTML_TABLE = """<html><body>
<table>
  <thead><tr><th>Name</th><th>Price</th><th>Stock</th></tr></thead>
  <tbody>
    <tr><td>Widget A</td><td>$9.99</td><td>In Stock</td></tr>
    <tr><td>Widget B</td><td>$19.99</td><td>Out of Stock</td></tr>
  </tbody>
</table>
</body></html>"""

def test_basic_table_extraction():
    tables = extract_tables(HTML_TABLE)
    assert len(tables) == 1
    rows = tables[0]
    assert len(rows) == 2
    assert rows[0]["Name"] == "Widget A"
    assert rows[0]["Price"] == "$9.99"

def test_empty_html():
    assert extract_tables("") == []

def test_no_tables():
    assert extract_tables("<p>No tables</p>") == []
