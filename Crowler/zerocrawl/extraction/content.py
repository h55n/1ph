"""
ZeroCrawl — Main Content Extraction
Uses trafilatura's scoring algorithm to identify main content vs. boilerplate.
"""
from __future__ import annotations

from typing import Optional

import trafilatura
from trafilatura.settings import use_config


# Trafilatura settings tuned for maximum recall
_CONFIG = use_config()
_CONFIG.set("DEFAULT", "EXTRACTION_TIMEOUT", "30")


def extract_main_content(
    raw_html: str,
    url: str = "",
    include_comments: bool = False,
    include_tables: bool = True,
    no_fallback: bool = False,
) -> dict:
    """
    Extract main content from raw HTML using trafilatura.
    Returns a dict with text, xml, and metadata.
    """
    result = {
        "text": "",
        "title": None,
        "author": None,
        "date": None,
        "description": None,
        "language": None,
        "tags": [],
        "categories": [],
    }

    if not raw_html:
        return result

    try:
        extracted = trafilatura.extract(
            raw_html,
            url=url or None,
            include_comments=include_comments,
            include_tables=include_tables,
            no_fallback=no_fallback,
            output_format="txt",
            config=_CONFIG,
        )
        if extracted:
            result["text"] = extracted
    except Exception:
        pass

    # Also try to get metadata via trafilatura
    try:
        meta = trafilatura.extract_metadata(raw_html, default_url=url or None)
        if meta:
            result["title"] = meta.title
            result["author"] = meta.author
            result["date"] = meta.date
            result["description"] = meta.description
            result["language"] = meta.language
            if meta.tags:
                result["tags"] = list(meta.tags) if hasattr(meta.tags, "__iter__") else []
            if meta.categories:
                result["categories"] = list(meta.categories) if hasattr(meta.categories, "__iter__") else []
    except Exception:
        pass

    return result


def extract_html_content(raw_html: str, url: str = "") -> str:
    """Extract main content as cleaned HTML (for conversion to markdown)."""
    if not raw_html:
        return ""
    try:
        result = trafilatura.extract(
            raw_html,
            url=url or None,
            include_tables=True,
            output_format="xml",
            config=_CONFIG,
        )
        return result or ""
    except Exception:
        return ""
