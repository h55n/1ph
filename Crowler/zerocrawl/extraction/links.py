"""
ZeroCrawl — Link Extraction & Classification
Classifies links as internal, external, pagination, or downloads.
"""
from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse

from .parser import get_all_links

_DOWNLOAD_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt",
    ".zip", ".tar", ".gz", ".rar", ".7z",
    ".mp3", ".mp4", ".avi", ".mov", ".mkv",
    ".csv", ".json", ".xml", ".yaml",
    ".exe", ".dmg", ".pkg", ".deb", ".rpm",
}

_PAGINATION_PATTERNS = [
    re.compile(r'[?&]page=\d+', re.I),
    re.compile(r'/page/\d+', re.I),
    re.compile(r'/p/\d+', re.I),
    re.compile(r'[?&]p=\d+', re.I),
    re.compile(r'[?&]offset=\d+', re.I),
    re.compile(r'[?&]start=\d+', re.I),
]

_PAGINATION_TEXT_PATTERNS = re.compile(
    r'^\s*(?:next|previous|prev|older|newer|›|‹|»|«|\d+)\s*$',
    re.I,
)


def _is_pagination(url: str, link_text: str) -> bool:
    for pattern in _PAGINATION_PATTERNS:
        if pattern.search(url):
            return True
    if _PAGINATION_TEXT_PATTERNS.match(link_text):
        return True
    return False


def _is_download(url: str) -> bool:
    path = urlparse(url).path.lower()
    return any(path.endswith(ext) for ext in _DOWNLOAD_EXTENSIONS)


def classify_links(
    raw_html: str,
    base_url: str,
) -> dict[str, list[str]]:
    """
    Extract and classify all links from raw HTML.
    Returns dict with keys: internal, external, pagination, downloads.
    """
    links = get_all_links(raw_html, base_url)
    base_parsed = urlparse(base_url)
    base_domain = base_parsed.netloc.lower()

    internal: list[str] = []
    external: list[str] = []
    pagination: list[str] = []
    downloads: list[str] = []

    seen: set[str] = set()

    for link in links:
        href = link["href"].strip()
        text = link["text"]

        # Resolve relative URLs
        try:
            resolved = urljoin(base_url, href)
        except Exception:
            continue

        if resolved in seen:
            continue
        seen.add(resolved)

        # Skip non-HTTP schemes
        parsed = urlparse(resolved)
        if parsed.scheme not in ("http", "https"):
            continue

        link_domain = parsed.netloc.lower()

        # Classify
        if _is_download(resolved):
            downloads.append(resolved)
        elif _is_pagination(resolved, text):
            pagination.append(resolved)
        elif link_domain == base_domain or link_domain.endswith("." + base_domain):
            internal.append(resolved)
        else:
            external.append(resolved)

    return {
        "internal": internal,
        "external": external,
        "pagination": pagination,
        "downloads": downloads,
    }
