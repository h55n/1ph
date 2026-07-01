"""
ZeroCrawl — Extraction Pipeline Orchestrator
Runs all extraction steps in sequence and assembles the final result blocks.
"""
from __future__ import annotations

import time
from typing import Any

from ..models import (
    ContentBlock,
    ImageItem,
    LinkBlock,
    MetadataBlock,
    PatternBlock,
    ScrapeResult,
    StructuredBlock,
)
from .cleaner import extract_plain_text, html_to_markdown
from .content import extract_main_content
from .images import extract_images
from .links import classify_links
from .metadata import extract_metadata
from .parser import pre_clean
from .patterns import detect_all_patterns
from .structured import extract_microdata, extract_open_graph, extract_schema_org, extract_twitter_card
from .tables import extract_tables


def run_pipeline(
    raw_html: str,
    url: str = "",
    final_url: str = "",
    fetch_mode: str = "unknown",
    timing_ms: int = 0,
    screenshot_b64: str | None = None,
) -> ScrapeResult:
    """
    Full extraction pipeline:
    1. Pre-clean HTML
    2. Extract metadata
    3. Extract main content (trafilatura)
    4. Extract structured data
    5. Build output formats
    6. Assemble ScrapeResult
    """
    if not raw_html:
        return ScrapeResult(
            url=url,
            final_url=final_url or url,
            status="failed",
            mode=fetch_mode,  # type: ignore
            error="Empty response body",
            error_type="parse_error",
            timing_ms=timing_ms,
        )

    # ── Step 1: Pre-clean ────────────────────────────────────────────────────
    cleaned_html = pre_clean(raw_html)

    # ── Step 2: Metadata ─────────────────────────────────────────────────────
    raw_meta = extract_metadata(raw_html, base_url=url)
    metadata = MetadataBlock(
        title=raw_meta.get("title"),
        description=raw_meta.get("description"),
        author=raw_meta.get("author"),
        published_date=raw_meta.get("published_date"),
        modified_date=raw_meta.get("modified_date"),
        language=raw_meta.get("language"),
        keywords=raw_meta.get("keywords", []),
        canonical_url=raw_meta.get("canonical_url"),
        favicon_url=raw_meta.get("favicon_url"),
        site_name=raw_meta.get("site_name"),
    )

    # ── Step 3: Main content extraction (trafilatura) ─────────────────────────
    content_data = extract_main_content(cleaned_html, url=url)
    main_text = content_data.get("text", "")

    # Fill in metadata gaps from trafilatura
    if not metadata.title and content_data.get("title"):
        metadata.title = content_data["title"]
    if not metadata.author and content_data.get("author"):
        metadata.author = content_data["author"]
    if not metadata.published_date and content_data.get("date"):
        metadata.published_date = content_data["date"]
    if not metadata.description and content_data.get("description"):
        metadata.description = content_data["description"]
    if not metadata.language and content_data.get("language"):
        metadata.language = content_data["language"]

    # ── Step 4: Structured extraction ─────────────────────────────────────────
    schema_org_data = extract_schema_org(raw_html)
    og_data = extract_open_graph(raw_html)
    tc_data = extract_twitter_card(raw_html)
    microdata = extract_microdata(raw_html)

    # Combine schema.org sources
    all_schema = schema_org_data + microdata

    table_data = extract_tables(cleaned_html)
    link_data = classify_links(cleaned_html, base_url=url)
    image_data = extract_images(cleaned_html, base_url=url)
    pattern_data = detect_all_patterns(main_text or cleaned_html)

    # ── Step 5: Build content formats ─────────────────────────────────────────
    markdown_text = html_to_markdown(cleaned_html)
    if not markdown_text and main_text:
        markdown_text = main_text
    plain_text = extract_plain_text(cleaned_html)
    if not plain_text:
        plain_text = main_text

    word_count = len(plain_text.split()) if plain_text else 0
    char_count = len(plain_text) if plain_text else 0

    # ── Step 6: Detect content status ─────────────────────────────────────────
    if word_count < 50:
        status = "partial"
    else:
        status = "success"

    # ── Step 7: Assemble ──────────────────────────────────────────────────────
    return ScrapeResult(
        url=url,
        final_url=final_url or url,
        status=status,  # type: ignore
        mode=fetch_mode,  # type: ignore
        timing_ms=timing_ms,
        content=ContentBlock(
            markdown=markdown_text,
            html=cleaned_html,
            text=plain_text,
            word_count=word_count,
            char_count=char_count,
        ),
        metadata=metadata,
        structured=StructuredBlock(
            schema_org=all_schema,
            open_graph=og_data,
            twitter_card=tc_data,
            tables=table_data,
            links=LinkBlock(**link_data),
            images=[
                ImageItem(
                    src=img["src"],
                    alt=img.get("alt", ""),
                    context=img.get("context", ""),
                    width=img.get("width"),
                    height=img.get("height"),
                )
                for img in image_data
            ],
            patterns=PatternBlock(**pattern_data),
        ),
        screenshot_b64=screenshot_b64,
    )
