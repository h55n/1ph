"""URL normalisation and deduplication."""
from __future__ import annotations
import hashlib
from urllib.parse import urlparse, urlencode, parse_qs

def normalise_url(url: str) -> str:
    try:
        p = urlparse(url.lower())
        qs = parse_qs(p.query)
        sorted_qs = urlencode(sorted(qs.items()), doseq=True)
        return p._replace(query=sorted_qs, fragment="", scheme=p.scheme or "https").geturl()
    except Exception:
        return url

def fingerprint(url: str) -> str:
    return hashlib.sha256(normalise_url(url).encode()).hexdigest()

class Deduplicator:
    def __init__(self):
        self._seen: set[str] = set()

    def is_seen(self, url: str) -> bool:
        fp = fingerprint(url)
        return fp in self._seen

    def mark_seen(self, url: str) -> None:
        self._seen.add(fingerprint(url))

    def check_and_mark(self, url: str) -> bool:
        """Returns True if new (not seen before), marks as seen."""
        fp = fingerprint(url)
        if fp in self._seen:
            return False
        self._seen.add(fp)
        return True

    def count(self) -> int:
        return len(self._seen)
