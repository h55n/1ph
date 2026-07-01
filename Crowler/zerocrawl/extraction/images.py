"""
ZeroCrawl — Image Extraction
Extracts images with src, alt, dimensions, and surrounding context text.
"""
from __future__ import annotations

from urllib.parse import urljoin

try:
    from selectolax.parser import HTMLParser
    _SL = True
except ImportError:
    _SL = False

# Skip images that are obviously decorative/noise
_SKIP_SRC_PATTERNS = [
    "data:image/gif;base64,R0lGOD",  # 1px tracking pixel
    "data:image/png;base64,iVBOR",   # tiny base64 PNGs
    "/assets/spacer",
    "/images/spacer",
    "blank.gif",
    "pixel.gif",
    "tracking",
]

_MIN_MEANINGFUL_DIMENSION = 50  # px — skip tiny images


def extract_images(raw_html: str, base_url: str = "") -> list[dict]:
    """
    Extract all meaningful images from HTML.
    Returns list of dicts with src, alt, context, width, height.
    """
    if not raw_html or not _SL:
        return []

    try:
        tree = HTMLParser(raw_html)
    except Exception:
        return []

    images = []
    seen_src = set()

    for img_node in tree.css("img"):
        attrs = img_node.attributes

        # Resolve src — support lazy loading patterns
        src = (
            attrs.get("src", "")
            or attrs.get("data-src", "")
            or attrs.get("data-lazy-src", "")
            or attrs.get("data-original", "")
            or ""
        ).strip()

        if not src:
            continue

        # Resolve relative
        if base_url and not src.startswith(("http://", "https://", "//")):
            src = urljoin(base_url, src)
        elif src.startswith("//"):
            src = "https:" + src

        # Skip tracking pixels and known noise
        if any(pattern in src for pattern in _SKIP_SRC_PATTERNS):
            continue

        if src in seen_src:
            continue
        seen_src.add(src)

        # Dimensions
        width = attrs.get("width")
        height = attrs.get("height")
        try:
            w = int(width) if width and str(width).isdigit() else None
        except (ValueError, TypeError):
            w = None
        try:
            h = int(height) if height and str(height).isdigit() else None
        except (ValueError, TypeError):
            h = None

        # Skip tiny images
        if w and h and w < _MIN_MEANINGFUL_DIMENSION and h < _MIN_MEANINGFUL_DIMENSION:
            continue

        alt = (attrs.get("alt") or "").strip()

        # Context: look at parent paragraph or figure caption
        context = _get_context(img_node)

        images.append({
            "src": src,
            "alt": alt,
            "context": context,
            "width": w,
            "height": h,
        })

    return images


def _get_context(img_node) -> str:
    """Try to find surrounding text context for this image."""
    try:
        # Walk up to find a paragraph, figure, or div with text
        parent = img_node.parent
        for _ in range(4):  # max 4 levels up
            if parent is None:
                break
            tag = (parent.tag or "").lower()
            if tag in ("p", "figure", "figcaption", "div", "article", "section"):
                text = parent.text(strip=True)
                if text and len(text) > 10:
                    return text[:200]
            parent = parent.parent
    except Exception:
        pass
    return ""
