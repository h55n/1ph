"""sitemap.xml parser."""
from __future__ import annotations
import re
from loguru import logger

async def fetch_sitemap_urls(base_url: str) -> list[str]:
    """Fetch and parse sitemap.xml (and sitemap_index.xml) for all page URLs."""
    from urllib.parse import urlparse
    from ..engine.fast import get_fast_fetcher
    parsed = urlparse(base_url)
    root = f"{parsed.scheme}://{parsed.netloc}"
    fetcher = get_fast_fetcher()
    urls: list[str] = []
    
    sitemap_urls_to_check = [f"{root}/sitemap.xml", f"{root}/sitemap_index.xml", f"{root}/robots.txt"]
    
    for sitemap_url in sitemap_urls_to_check[:2]:
        try:
            result = await fetcher.fetch(sitemap_url, timeout=15)
            if result.get("status_code") == 200 and result.get("html"):
                found = _parse_sitemap_xml(result["html"])
                # Recurse into sitemap index
                sub_sitemaps = [u for u in found if u.endswith(".xml")]
                page_urls = [u for u in found if not u.endswith(".xml")]
                urls.extend(page_urls)
                for sub in sub_sitemaps[:5]:
                    try:
                        sub_result = await fetcher.fetch(sub, timeout=15)
                        if sub_result.get("status_code") == 200:
                            sub_found = _parse_sitemap_xml(sub_result.get("html", ""))
                            urls.extend([u for u in sub_found if not u.endswith(".xml")])
                    except Exception:
                        pass
        except Exception as e:
            logger.debug(f"Sitemap fetch error for {sitemap_url}: {e}")
    
    return list(dict.fromkeys(urls))  # dedup preserving order

def _parse_sitemap_xml(xml: str) -> list[str]:
    """Extract all <loc> URLs from sitemap XML."""
    return re.findall(r'<loc>\s*(https?://[^\s<]+)\s*</loc>', xml, re.IGNORECASE)
