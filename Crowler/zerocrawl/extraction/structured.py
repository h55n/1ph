"""
ZeroCrawl — Structured Data Extraction
Schema.org JSON-LD, Open Graph, Twitter Card, and HTML Microdata.
"""
from __future__ import annotations

import json
import re
from typing import Any

try:
    from selectolax.parser import HTMLParser
    _SL = True
except ImportError:
    _SL = False


def extract_schema_org(raw_html: str) -> list[dict[str, Any]]:
    """
    Extract all JSON-LD blocks from <script type="application/ld+json">.
    Returns list of parsed dicts.
    """
    results = []
    if not raw_html:
        return results

    pattern = re.compile(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        re.DOTALL | re.IGNORECASE,
    )
    for match in pattern.finditer(raw_html):
        raw = match.group(1).strip()
        if not raw:
            continue
        try:
            obj = json.loads(raw)
            if isinstance(obj, list):
                results.extend(obj)
            elif isinstance(obj, dict):
                results.append(obj)
        except json.JSONDecodeError:
            # Try to fix common issues
            try:
                raw_fixed = re.sub(r",\s*}", "}", re.sub(r",\s*]", "]", raw))
                obj = json.loads(raw_fixed)
                if isinstance(obj, list):
                    results.extend(obj)
                elif isinstance(obj, dict):
                    results.append(obj)
            except Exception:
                pass

    return results


def extract_open_graph(raw_html: str) -> dict[str, str]:
    """Extract Open Graph meta tags."""
    og: dict[str, str] = {}
    if not raw_html or not _SL:
        return og
    try:
        tree = HTMLParser(raw_html)
        for node in tree.css("meta[property^='og:']"):
            prop = node.attributes.get("property", "")
            content = node.attributes.get("content", "")
            if prop and content:
                og[prop[3:]] = content
    except Exception:
        pass
    return og


def extract_twitter_card(raw_html: str) -> dict[str, str]:
    """Extract Twitter Card meta tags."""
    tc: dict[str, str] = {}
    if not raw_html or not _SL:
        return tc
    try:
        tree = HTMLParser(raw_html)
        for node in tree.css("meta[name^='twitter:']"):
            name = node.attributes.get("name", "")
            content = node.attributes.get("content", "")
            if name and content:
                tc[name[8:]] = content
    except Exception:
        pass
    return tc


def extract_microdata(raw_html: str) -> list[dict[str, Any]]:
    """Extract HTML Microdata (itemprop/itemscope/itemtype)."""
    items = []
    if not raw_html or not _SL:
        return items
    try:
        tree = HTMLParser(raw_html)
        for scope_node in tree.css("[itemscope]"):
            item: dict[str, Any] = {}
            itemtype = scope_node.attributes.get("itemtype", "")
            if itemtype:
                item["@type"] = itemtype.split("/")[-1] if "/" in itemtype else itemtype

            for prop_node in scope_node.css("[itemprop]"):
                prop_name = prop_node.attributes.get("itemprop", "")
                if not prop_name:
                    continue
                # Extract value from various element types
                tag = prop_node.tag.lower()
                if tag in ("meta",):
                    value = prop_node.attributes.get("content", "")
                elif tag in ("link", "a"):
                    value = prop_node.attributes.get("href", "") or prop_node.text(strip=True)
                elif tag == "img":
                    value = prop_node.attributes.get("src", "")
                elif tag == "time":
                    value = prop_node.attributes.get("datetime", "") or prop_node.text(strip=True)
                else:
                    value = prop_node.text(strip=True) or ""

                if value:
                    if prop_name in item:
                        if isinstance(item[prop_name], list):
                            item[prop_name].append(value)
                        else:
                            item[prop_name] = [item[prop_name], value]
                    else:
                        item[prop_name] = value

            if len(item) > 1:  # more than just @type
                items.append(item)
    except Exception:
        pass
    return items
