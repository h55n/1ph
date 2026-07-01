from fastapi import APIRouter
from ...api.schemas import MapRequest
from ...crawl.sitemap import fetch_sitemap_urls
from ...engine.orchestrator import get_orchestrator
from ...extraction.links import classify_links
from ...models import ScrapeOptions

router = APIRouter(tags=["map"])

@router.post("/map")
async def map_urls(req: MapRequest):
    urls = await fetch_sitemap_urls(req.url) if req.include_sitemap else []
    if not urls:
        result = await get_orchestrator().scrape(req.url, ScrapeOptions(mode="fast"))
        urls = classify_links(result.content.html, req.url).get("internal", [])
    urls = list(dict.fromkeys(urls))
    return {"url": req.url, "urls": urls, "count": len(urls)}
