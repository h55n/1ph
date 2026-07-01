"""
ZeroCrawl — Pattern Detection Engine
Regex + heuristic detection of common data patterns.
"""
from __future__ import annotations

import re
from typing import Any


# ──────────────────────────────────────────────────────────────────────────────
# Email
# ──────────────────────────────────────────────────────────────────────────────
_EMAIL_RE = re.compile(
    r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b'
)

# ──────────────────────────────────────────────────────────────────────────────
# Phone — international & US-centric patterns
# ──────────────────────────────────────────────────────────────────────────────
_PHONE_RE = re.compile(
    r'(?:(?:\+|00)\d{1,3}[\s\-.]?)?\(?\d{2,4}\)?[\s\-.]?\d{2,4}[\s\-.]?\d{2,9}',
)
_PHONE_MIN_DIGITS = 7

# ──────────────────────────────────────────────────────────────────────────────
# Price patterns
# ──────────────────────────────────────────────────────────────────────────────
_CURRENCY_SYMBOLS = r'[$€£¥₹₩₺฿₫₪R]'
_CURRENCY_CODES = r'(?:USD|EUR|GBP|JPY|CAD|AUD|CHF|CNY|INR|KRW|MXN|BRL|SGD|HKD)'
_PRICE_RE = re.compile(
    r'(?:' + _CURRENCY_SYMBOLS + r'|' + _CURRENCY_CODES + r'\s?)[\d,]+(?:\.\d{1,4})?'
    r'|[\d,]+(?:\.\d{1,4})?\s?(?:' + _CURRENCY_SYMBOLS + r'|' + _CURRENCY_CODES + r')',
)

_SYMBOL_TO_CODE = {
    "$": "USD", "€": "EUR", "£": "GBP", "¥": "JPY",
    "₹": "INR", "₩": "KRW", "₺": "TRY", "฿": "THB",
    "₫": "VND", "₪": "ILS", "R": "ZAR",
}

# ──────────────────────────────────────────────────────────────────────────────
# URL (excluding those already extracted as links)
# ──────────────────────────────────────────────────────────────────────────────
_URL_RE = re.compile(
    r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    r'(?:/[^\s<>"{}|\\^`\[\]]*)?',
)

# ──────────────────────────────────────────────────────────────────────────────
# Social handles
# ──────────────────────────────────────────────────────────────────────────────
_SOCIAL_PATTERNS = {
    "twitter": re.compile(r'(?:twitter\.com|x\.com)/(@?[\w]{1,15})'),
    "instagram": re.compile(r'instagram\.com/(?!p/)(@?[\w.]{1,30})'),
    "linkedin": re.compile(r'linkedin\.com/(?:in|company)/([\w\-]+)'),
    "facebook": re.compile(r'facebook\.com/([\w.]+)'),
    "github": re.compile(r'github\.com/([\w\-]{1,39})'),
    "youtube": re.compile(r'youtube\.com/(?:@|channel/|user/)([\w\-]+)'),
    "tiktok": re.compile(r'tiktok\.com/@([\w.]+)'),
}


def find_emails(text: str) -> list[str]:
    """Find all email addresses in text."""
    found = _EMAIL_RE.findall(text)
    # Deduplicate preserving order
    seen = set()
    result = []
    for e in found:
        e = e.lower()
        if e not in seen:
            seen.add(e)
            result.append(e)
    return result


def find_phones(text: str) -> list[str]:
    """Find all phone numbers in text (loose match)."""
    candidates = _PHONE_RE.findall(text)
    result = []
    seen = set()
    for candidate in candidates:
        digits = re.sub(r'\D', '', candidate)
        if len(digits) >= _PHONE_MIN_DIGITS and candidate not in seen:
            seen.add(candidate)
            result.append(candidate.strip())
    return result


def find_prices(text: str) -> list[dict[str, Any]]:
    """Find all prices in text, returning amount+currency dicts."""
    matches = _PRICE_RE.findall(text)
    result = []
    seen = set()
    for match in matches:
        match = match.strip()
        if match in seen:
            continue
        seen.add(match)

        # Extract numeric part
        numeric_str = re.sub(r'[^\d.,]', '', match).replace(",", "")
        try:
            amount = float(numeric_str)
        except (ValueError, TypeError):
            continue

        # Determine currency
        currency = "USD"  # default
        for symbol, code in _SYMBOL_TO_CODE.items():
            if symbol in match:
                currency = code
                break
        else:
            for code in ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "INR", "KRW"]:
                if code in match:
                    currency = code
                    break

        result.append({"amount": amount, "currency": currency, "raw": match})

    return result


def find_dates(text: str) -> list[str]:
    """Find date strings and return as ISO 8601 where possible."""
    import dateparser

    # Common date patterns for fast detection
    patterns = [
        r'\b\d{4}-\d{2}-\d{2}\b',                        # 2024-01-15
        r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',                  # 01/15/2024
        r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b',
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b',
    ]

    candidates = []
    for pat in patterns:
        candidates.extend(re.findall(pat, text, re.IGNORECASE))

    result = []
    seen = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        try:
            dt = dateparser.parse(candidate, settings={"RETURN_AS_TIMEZONE_AWARE": False})
            if dt and 1970 <= dt.year <= 2100:
                result.append(dt.strftime("%Y-%m-%d"))
        except Exception:
            pass

    return list(dict.fromkeys(result))  # dedup preserving order


def find_urls(text: str) -> list[str]:
    """Find all URLs in text."""
    found = _URL_RE.findall(text)
    seen = set()
    result = []
    for url in found:
        if url not in seen:
            seen.add(url)
            result.append(url)
    return result


def find_social_handles(text: str) -> dict[str, str]:
    """Find social media profile handles/URLs."""
    handles: dict[str, str] = {}
    for platform, pattern in _SOCIAL_PATTERNS.items():
        m = pattern.search(text)
        if m:
            handle = m.group(1).lstrip("@")
            handles[platform] = f"@{handle}"
    return handles


def detect_all_patterns(text: str) -> dict:
    """Run all pattern detectors on text. Returns PatternBlock-compatible dict."""
    return {
        "emails": find_emails(text),
        "phones": find_phones(text),
        "prices": find_prices(text),
        "dates": find_dates(text),
        "urls": find_urls(text),
        "social_handles": find_social_handles(text),
    }
