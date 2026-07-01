import pytest
from zerocrawl.extraction.patterns import find_emails, find_phones, find_prices, find_urls

TEXT = """
Contact us at hello@example.com or support@company.org
Call +1 (555) 123-4567
Products from $29.99 available
Visit https://example.com and https://docs.example.com/guide
"""

def test_find_emails():
    emails = find_emails(TEXT)
    assert "hello@example.com" in emails
    assert "support@company.org" in emails

def test_find_emails_dedup():
    emails = find_emails("email@test.com email@test.com")
    assert emails.count("email@test.com") == 1

def test_find_prices():
    prices = find_prices(TEXT)
    assert len(prices) >= 1
    amounts = [p["amount"] for p in prices]
    assert 29.99 in amounts

def test_find_urls():
    urls = find_urls(TEXT)
    assert any("example.com" in u for u in urls)

def test_no_false_positives():
    emails = find_emails("no emails here just text 123 foo@")
    assert len(emails) == 0
