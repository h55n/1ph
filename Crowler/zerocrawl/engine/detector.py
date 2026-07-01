"""
ZeroCrawl — JS Rendering Detector
Heuristics to detect if a page was rendered client-side and needs a browser.
"""
from __future__ import annotations

import re

# Signals that strongly suggest the page requires JavaScript execution
_JS_SIGNALS = [
    # React / Next.js
    "__NEXT_DATA__",
    "react-root",
    "__REACT_DEVTOOLS",
    "data-reactroot",
    # Vue
    "__VUE__",
    "data-v-app",
    # Angular
    "ng-version",
    "ng-app",
    # Generic SPA empty root
    '<div id="root"></div>',
    '<div id="app"></div>',
    '<div id="__nuxt">',
    # Svelte
    "<script>var __svelte",
    # Gatsby
    "___gatsby",
    # Ember
    "data-ember-action",
    # Cloudflare JS challenge
    "cf-browser-verification",
    "cf_chl_opt",
    "challenge-platform",
    # DataDome
    "datadome",
    # PerimeterX
    "_pxAppId",
    # Akamai
    "ak_bmsc",
]

# If visible text is under this threshold, suspect JS rendering
_MIN_TEXT_CHARS = 500

# Bot detection body patterns (blocking page, not just JS rendering)
_BLOCK_SIGNALS = [
    "Access Denied",
    "Enable JavaScript",
    "Please enable JavaScript",
    "Just a moment...",
    "Checking your browser",
    "DDoS protection by Cloudflare",
    "cf-browser-verification",
    "cf_chl_opt",
    "Ray ID",
    "Please Wait... | Cloudflare",
    "403 Forbidden",
    "captcha-challenge",
    "g-recaptcha",
    "h-captcha",
]


def detect_js_required(html: str, status_code: int = 200) -> dict:
    """
    Analyse a raw HTML response and determine if JS rendering is needed.

    Returns:
        {
          "needs_browser": bool,
          "is_blocked": bool,
          "has_captcha": bool,
          "signals": list of matched signals,
        }
    """
    result = {
        "needs_browser": False,
        "is_blocked": False,
        "has_captcha": False,
        "signals": [],
    }

    if not html:
        result["needs_browser"] = True
        result["signals"].append("empty_body")
        return result

    # Check HTTP status codes that suggest blocking
    if status_code in (403, 429, 503, 502):
        result["is_blocked"] = True
        result["signals"].append(f"http_{status_code}")

    # Check for captcha
    captcha_patterns = ["g-recaptcha", "h-captcha", "captcha-challenge", "recaptcha"]
    for pat in captcha_patterns:
        if pat in html.lower():
            result["has_captcha"] = True
            result["is_blocked"] = True
            result["signals"].append("captcha")
            break

    # Check JS rendering signals
    for signal in _JS_SIGNALS:
        if signal in html:
            result["needs_browser"] = True
            result["signals"].append(signal)

    # Check visible text volume
    visible_text = re.sub(r'<[^>]+>', '', html)
    visible_text = re.sub(r'\s+', ' ', visible_text).strip()
    if len(visible_text) < _MIN_TEXT_CHARS:
        result["needs_browser"] = True
        result["signals"].append(f"low_text_length:{len(visible_text)}")

    # Check block signals
    for signal in _BLOCK_SIGNALS:
        if signal in html:
            result["is_blocked"] = True
            result["signals"].append(f"block:{signal}")

    return result
