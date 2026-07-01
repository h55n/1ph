"""
ZeroCrawl — TLS Fingerprint Profile Selection
Maps our impersonate profile names to curl_cffi impersonate strings.
"""
from __future__ import annotations

# Maps ZeroCrawl profile names → curl_cffi impersonate target strings
CURL_CFFI_MAP: dict[str, str] = {
    "chrome120": "chrome120",
    "chrome119": "chrome119",
    "chrome118": "chrome118",
    "chrome116": "chrome116",
    "firefox121": "firefox121",
    "firefox120": "firefox120",
    "safari17": "safari17_2",
    "safari16": "safari16",
    "edge120": "edge120",
}

# Ordered list from most common to least (weighted rotation)
_WEIGHTED_PROFILES = [
    "chrome120",  # ~33% market share
    "chrome120",
    "chrome120",
    "chrome119",  # ~15%
    "chrome119",
    "edge120",    # ~5%
    "firefox121", # ~4%
    "safari17",   # ~3%
]


def get_curl_cffi_target(impersonate: str) -> str:
    """Return the curl_cffi impersonate string for a profile name."""
    return CURL_CFFI_MAP.get(impersonate, "chrome120")


def get_weighted_random_profile() -> str:
    """Return a weighted-random profile (session-level, not per-request)."""
    import random
    return random.choice(_WEIGHTED_PROFILES)
