"""
ZeroCrawl — robots.txt Handling
Fetch, parse, cache, and enforce robots.txt per domain.
"""
from __future__ import annotations

import time
import urllib.robotparser
from urllib.parse import urlparse

USER_AGENT = "ZeroCrawl/1.0 (+https://github.com/zerocrawl/zerocrawl)"

# In-memory cache: domain → (RobotFileParser, fetch_timestamp)
_cache: dict[str, tuple[urllib.robotparser.RobotFileParser, float]] = {}
_CACHE_TTL = 3600  # 1 hour


def _get_parser(domain: str, scheme: str = "https") -> urllib.robotparser.RobotFileParser | None:
    now = time.time()
    cached = _cache.get(domain)
    if cached and (now - cached[1]) < _CACHE_TTL:
        return cached[0]

    robots_url = f"{scheme}://{domain}/robots.txt"
    parser = urllib.robotparser.RobotFileParser()
    parser.set_url(robots_url)
    try:
        parser.read()
        _cache[domain] = (parser, now)
        return parser
    except Exception:
        # Can't read robots.txt → treat as "all allowed"
        _cache[domain] = (None, now)  # type: ignore
        return None


def is_allowed(url: str, user_agent: str = "*") -> bool:
    """Return True if the URL is allowed to be scraped per robots.txt."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        scheme = parsed.scheme or "https"
        parser = _get_parser(domain, scheme)
        if parser is None:
            return True
        return parser.can_fetch(user_agent, url)
    except Exception:
        return True  # fail open


def get_crawl_delay(url: str, user_agent: str = "*") -> float | None:
    """Return the crawl-delay directive for this domain, or None."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        scheme = parsed.scheme or "https"
        parser = _get_parser(domain, scheme)
        if parser is None:
            return None
        return parser.crawl_delay(user_agent)
    except Exception:
        return None
