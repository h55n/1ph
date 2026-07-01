"""Extraction prompt templates."""
from __future__ import annotations
import json
from typing import Any

_TEMPLATES = {
    "generic_extract": """You are a precise data extractor. Extract the requested fields from the content below.
Return ONLY a valid JSON object matching the schema. No explanations, no markdown, no preamble.

SCHEMA:
{schema}

CONTENT:
{content}

JSON:""",

    "product_extract": """Extract product details from this e-commerce page content.
Return ONLY a valid JSON object matching the schema. No explanations.

SCHEMA:
{schema}

CONTENT:
{content}

JSON:""",

    "article_extract": """Extract article/news metadata from this page content.
Return ONLY a valid JSON object matching the schema. No explanations.

SCHEMA:
{schema}

CONTENT:
{content}

JSON:""",

    "contact_extract": """Extract contact information from this page content.
Return ONLY a valid JSON object matching the schema. No explanations.

SCHEMA:
{schema}

CONTENT:
{content}

JSON:""",

    "listing_extract": """Extract all items from this listing/directory page.
Return ONLY a valid JSON array, where each element matches the schema. No explanations.

SCHEMA (per item):
{schema}

CONTENT:
{content}

JSON array:""",
}

def get_prompt(template: str, content: str, schema: dict[str, Any]) -> str:
    tmpl = _TEMPLATES.get(template, _TEMPLATES["generic_extract"])
    return tmpl.format(
        schema=json.dumps(schema, indent=2),
        content=content[:8000],  # truncate to avoid token limits
    )

def detect_template(schema: dict[str, Any]) -> str:
    keys = set(str(k).lower() for k in schema.keys())
    if keys & {"price", "sku", "availability", "in_stock"}:
        return "product_extract"
    if keys & {"headline", "article", "author", "published"}:
        return "article_extract"
    if keys & {"email", "phone", "address", "contact"}:
        return "contact_extract"
    if "items" in keys or "listings" in keys:
        return "listing_extract"
    return "generic_extract"
