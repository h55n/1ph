"""
ZeroCrawl — Metadata Extraction
Extracts title, description, author, dates, canonical URL, language, favicon,
Open Graph tags, Twitter Card tags, and site name from HTML.
"""
from __future__ import annotations

import re
from typing import Optional
from urllib.parse import urljoin, urlparse

try:
    from selectolax.parser import HTMLParser
    _SL = True
except ImportError:
    _SL = False


def _text(node) -> str:
    if node is None:
        return ""
    return (node.text(strip=True) or node.attributes.get("content", "") or "").strip()


def _attr(node, attr: str, default: str = "") -> str:
    if node is None:
        return default
    return (node.attributes.get(attr) or default).strip()


def extract_metadata(raw_html: str, base_url: str = "") -> dict:
    """
    Extract all metadata from HTML head.
    Returns a flat dict with standardised keys.
    """
    meta: dict = {
        "title": None,
        "description": None,
        "author": None,
        "published_date": None,
        "modified_date": None,
        "language": None,
        "keywords": [],
        "canonical_url": None,
        "favicon_url": None,
        "site_name": None,
        "open_graph": {},
        "twitter_card": {},
    }

    if not raw_html or not _SL:
        return meta

    try:
        tree = HTMLParser(raw_html)
    except Exception:
        return meta

    # ── Title ─────────────────────────────────────────────────────────────────
    title_node = tree.css_first("title")
    if title_node:
        meta["title"] = title_node.text(strip=True) or None

    # ── Language ──────────────────────────────────────────────────────────────
    html_node = tree.css_first("html")
    if html_node:
        lang = html_node.attributes.get("lang", "")
        if lang:
            meta["language"] = lang.split("-")[0].lower()

    # ── Canonical ─────────────────────────────────────────────────────────────
    canonical = tree.css_first("link[rel='canonical']")
    if canonical:
        href = canonical.attributes.get("href", "")
        if href:
            meta["canonical_url"] = urljoin(base_url, href)

    # ── Favicon ───────────────────────────────────────────────────────────────
    favicon_node = (
        tree.css_first("link[rel='icon']")
        or tree.css_first("link[rel='shortcut icon']")
        or tree.css_first("link[rel='apple-touch-icon']")
    )
    if favicon_node:
        href = favicon_node.attributes.get("href", "")
        if href:
            meta["favicon_url"] = urljoin(base_url, href)
    elif base_url:
        parsed = urlparse(base_url)
        meta["favicon_url"] = f"{parsed.scheme}://{parsed.netloc}/favicon.ico"

    # ── Standard <meta> tags ──────────────────────────────────────────────────
    for node in tree.css("meta"):
        attrs = node.attributes
        name = (attrs.get("name") or "").lower().strip()
        prop = (attrs.get("property") or "").lower().strip()
        content = (attrs.get("content") or "").strip()

        if not content:
            continue

        # Standard meta (by name attribute)
        if name == "description" and not meta["description"]:
            meta["description"] = content
        elif name == "author" and not meta["author"]:
            meta["author"] = content
        elif name == "keywords":
            meta["keywords"] = [k.strip() for k in content.split(",") if k.strip()]
        elif name in ("date", "pubdate", "datePublished"):
            if not meta["published_date"]:
                meta["published_date"] = _parse_date_str(content)
        elif name in ("last-modified", "dateModified"):
            if not meta["modified_date"]:
                meta["modified_date"] = _parse_date_str(content)

        # article: properties (by property attribute)
        if prop == "article:published_time":
            if not meta["published_date"]:
                meta["published_date"] = _parse_date_str(content)
        elif prop == "article:modified_time":
            if not meta["modified_date"]:
                meta["modified_date"] = _parse_date_str(content)
        elif prop == "article:author":
            if not meta["author"]:
                meta["author"] = content

        # Open Graph
        if prop.startswith("og:"):
            key = prop[3:]
            meta["open_graph"][key] = content
        # Twitter Card
        elif prop.startswith("twitter:") or name.startswith("twitter:"):
            key = (prop or name)[8:]
            meta["twitter_card"][key] = content

    # ── Override title/description from OG if not found ──────────────────────
    og = meta["open_graph"]
    tc = meta["twitter_card"]

    if not meta["title"]:
        meta["title"] = og.get("title") or tc.get("title")
    if not meta["description"]:
        meta["description"] = og.get("description") or tc.get("description")
    if not meta["author"]:
        meta["author"] = og.get("article:author") or tc.get("creator")
    if not meta["site_name"]:
        meta["site_name"] = og.get("site_name")
    if not meta["published_date"]:
        pub = og.get("article:published_time") or og.get("published_time")
        if pub:
            meta["published_date"] = _parse_date_str(pub)
    if not meta["modified_date"]:
        mod = og.get("article:modified_time") or og.get("modified_time")
        if mod:
            meta["modified_date"] = _parse_date_str(mod)

    return meta


def _parse_date_str(value: str) -> Optional[str]:
    """Try to parse a date string to ISO 8601. Returns None on failure."""
    if not value:
        return None
    # Already ISO-ish
    iso_match = re.match(r"(\d{4}-\d{2}-\d{2})", value)
    if iso_match:
        return iso_match.group(1)
    # Try dateparser as a fallback
    try:
        import dateparser
        dt = dateparser.parse(value, settings={"RETURN_AS_TIMEZONE_AWARE": False})
        if dt:
            return dt.strftime("%Y-%m-%d")
    except Exception:
        pass
    return None
