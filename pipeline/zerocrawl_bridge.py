"""
zerocrawl_bridge.py — Synchronous bridge for extraction.
NOTE: This previously utilized ZeroCrawl but has been refactored to use the 
Jina Reader API to remove heavy Playwright dependency overhead while maintaining
the exact same API contract for the rest of the pipeline.

Provides three helpers:
  - fetch_html(url, ...)       → raw HTML string (or empty string on failure)
  - fetch_markdown(url, ...)   → clean markdown string
  - fetch_js_page(url, ...)    → JS-rendered HTML (browser mode, guaranteed)
"""
from __future__ import annotations

import os
import httpx
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Jina API Key for higher rate limits
JINA_API_KEY = os.environ.get("JINA_API_KEY", "").strip()

# Default settings
DEFAULT_TIMEOUT = 60

def _do_jina_request(url: str, format_type: str, timeout: int, wait_for_selector: Optional[str] = None) -> str:
    """Make the actual request to Jina Reader API."""
    jina_url = f"https://r.jina.ai/{url}"
    
    headers = {
        "Accept": "application/json",
        "X-Respond-With": format_type,
        "X-Timeout": str(timeout)
    }
    
    if JINA_API_KEY:
        headers["Authorization"] = f"Bearer {JINA_API_KEY}"
        
    if wait_for_selector:
        headers["X-Wait-For-Selector"] = wait_for_selector

    try:
        with httpx.Client(timeout=timeout + 5, follow_redirects=True) as client:
            r = client.get(jina_url, headers=headers)
            
            if r.status_code >= 400:
                print(f"[jina_bridge] HTTP {r.status_code} for {url} (format={format_type})")
                return ""
            
            try:
                data = r.json()
                if data and "data" in data:
                    if format_type == "html":
                        return data["data"].get("html", "")
                    else:
                        return data["data"].get("content", "")
            except Exception:
                # If they didn't respect application/json, fallback to plain text
                return r.text
                
            return ""
    except Exception as e:
        print(f"[jina_bridge] Request failed for {url}: {e}")
        return ""


def fetch_html(
    url: str,
    mode: str = "auto",
    timeout: int = DEFAULT_TIMEOUT,
    cache_ttl: int = 3600,
    force_refresh: bool = False,
    wait_for_selector: Optional[str] = None,
) -> str:
    """
    Fetch a URL and return raw HTML using Jina.
    """
    return _do_jina_request(url, format_type="html", timeout=timeout, wait_for_selector=wait_for_selector)


def fetch_markdown(
    url: str,
    mode: str = "auto",
    timeout: int = DEFAULT_TIMEOUT,
    cache_ttl: int = 3600,
    force_refresh: bool = False,
    wait_for_selector: Optional[str] = None,
) -> str:
    """
    Fetch a URL and return clean markdown using Jina.
    """
    return _do_jina_request(url, format_type="markdown", timeout=timeout, wait_for_selector=wait_for_selector)


def fetch_js_page(
    url: str,
    wait_for_selector: Optional[str] = None,
    timeout: int = 90,
    cache_ttl: int = 3600,
) -> str:
    """
    Fetch JS-rendered HTML using Jina. Jina does JS rendering natively.
    """
    return _do_jina_request(url, format_type="html", timeout=timeout, wait_for_selector=wait_for_selector)
