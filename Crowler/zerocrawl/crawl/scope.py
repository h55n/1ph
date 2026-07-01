"""Domain scope enforcement for crawls."""
from __future__ import annotations
import re
from urllib.parse import urlparse

class ScopeFilter:
    def __init__(self, start_url: str, same_domain: bool = True, same_subdomain: bool = False,
                 include_patterns: list[str] = None, exclude_patterns: list[str] = None):
        parsed = urlparse(start_url)
        self.base_domain = parsed.netloc.lower().split(":")[0]
        # Extract root domain (strip subdomain)
        parts = self.base_domain.split(".")
        self.root_domain = ".".join(parts[-2:]) if len(parts) > 1 else self.base_domain
        self.same_domain = same_domain
        self.same_subdomain = same_subdomain
        self._include = [re.compile(self._glob_to_re(p)) for p in (include_patterns or [])]
        self._exclude = [re.compile(self._glob_to_re(p)) for p in (exclude_patterns or [])]

    @staticmethod
    def _glob_to_re(pattern: str) -> str:
        return re.escape(pattern).replace(r"\*", ".*")

    def is_in_scope(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                return False
            domain = parsed.netloc.lower().split(":")[0]
            if self.same_subdomain and domain != self.base_domain:
                return False
            if self.same_domain:
                if domain != self.base_domain and not domain.endswith("." + self.root_domain):
                    return False
            path = parsed.path
            for pat in self._exclude:
                if pat.search(url):
                    return False
            if self._include:
                return any(pat.search(url) for pat in self._include)
            return True
        except Exception:
            return False
