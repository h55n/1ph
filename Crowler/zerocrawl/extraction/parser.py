"""
ZeroCrawl — HTML Parser
selectolax-based DOM parsing and pre-cleaning step.
"""
from __future__ import annotations

from typing import Optional

try:
    from selectolax.parser import HTMLParser, Node
    _SELECTOLAX = True
except ImportError:
    from html.parser import HTMLParser as _StdHTMLParser  # type: ignore
    _SELECTOLAX = False

# Tags that are always noise — remove unconditionally
_REMOVE_TAGS = {
    "script", "style", "noscript", "svg", "canvas",
    "iframe", "object", "embed", "applet",
    "meta", "link", "head",
    "nav", "footer", "header",  # structural boilerplate
    "aside",
    "form", "input", "button", "select", "textarea",
    "figure",  # keep? PRD says remove; we'll keep but strip captions
}

# Tags we clean but preserve their text content
_UNWRAP_TAGS = {"span", "div", "section", "article", "main"}


def parse_html(raw_html: str) -> "HTMLParser":  # type: ignore
    """Parse raw HTML with selectolax (C speed)."""
    if not _SELECTOLAX:
        raise RuntimeError("selectolax is not installed. Run: pip install selectolax")
    return HTMLParser(raw_html)


def pre_clean(raw_html: str) -> str:
    """
    Remove definitely-useless elements from the HTML.
    Returns cleaned HTML string.
    """
    if not _SELECTOLAX:
        return raw_html

    try:
        tree = HTMLParser(raw_html)
    except Exception:
        return raw_html

    for tag in _REMOVE_TAGS:
        for node in tree.css(tag):
            try:
                node.decompose()
            except Exception:
                pass

    # Remove elements that are visually hidden (aria-hidden, display:none patterns)
    for node in tree.css("[aria-hidden='true']"):
        try:
            node.decompose()
        except Exception:
            pass

    # Remove cookie banners and common noise by id/class patterns
    noise_patterns = [
        "[id*='cookie']", "[class*='cookie']",
        "[id*='banner']", "[class*='banner']",
        "[id*='popup']", "[class*='popup']",
        "[class*='advertisement']", "[class*='ads']",
        "[id*='overlay']", "[class*='overlay']",
    ]
    for selector in noise_patterns:
        for node in tree.css(selector):
            try:
                node.decompose()
            except Exception:
                pass

    return tree.html or raw_html


def extract_text(raw_html: str, separator: str = "\n") -> str:
    """Extract all visible text from HTML, flat."""
    if not _SELECTOLAX:
        return raw_html

    try:
        tree = HTMLParser(raw_html)
        return tree.text(separator=separator, strip=True)
    except Exception:
        return ""


def get_all_links(raw_html: str, base_url: str = "") -> list[dict]:
    """Extract all anchor tags with href and text."""
    if not _SELECTOLAX:
        return []

    try:
        tree = HTMLParser(raw_html)
        links = []
        for node in tree.css("a[href]"):
            href = node.attributes.get("href", "").strip()
            text = (node.text(strip=True) or "").strip()
            if href and not href.startswith(("#", "javascript:", "mailto:", "tel:")):
                links.append({"href": href, "text": text})
        return links
    except Exception:
        return []


def get_all_images(raw_html: str) -> list[dict]:
    """Extract img tags with src, alt, data-src, width, height."""
    if not _SELECTOLAX:
        return []

    try:
        tree = HTMLParser(raw_html)
        images = []
        for node in tree.css("img"):
            src = (
                node.attributes.get("src", "")
                or node.attributes.get("data-src", "")
                or node.attributes.get("data-lazy-src", "")
                or ""
            ).strip()
            if not src:
                continue
            alt = node.attributes.get("alt", "").strip()
            width = node.attributes.get("width")
            height = node.attributes.get("height")
            images.append({
                "src": src,
                "alt": alt,
                "width": int(width) if width and width.isdigit() else None,
                "height": int(height) if height and height.isdigit() else None,
            })
        return images
    except Exception:
        return []
