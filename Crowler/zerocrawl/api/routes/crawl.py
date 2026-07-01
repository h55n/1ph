from fastapi import APIRouter, HTTPException
from ...api.schemas import CrawlRequest
from ...models import CrawlOptions
from ...crawl.crawler import SiteCrawler
import asyncio, uuid

router = APIRouter(tags=["crawl"])
_active: dict = {}

@router.post("/crawl")
async def start_crawl(req: CrawlRequest):
    crawl_id = str(uuid.uuid4())
    options = CrawlOptions(start_url=req.start_url, max_depth=req.max_depth,
                            max_pages=req.max_pages, concurrency=req.concurrency,
                            same_domain=req.same_domain, include_patterns=req.include_patterns,
                            exclude_patterns=req.exclude_patterns)
    results = []
    async def run():
        async for r in SiteCrawler(options).crawl():
            results.append(r.model_dump(mode="json"))
        _active[crawl_id]["status"] = "completed"
    _active[crawl_id] = {"status": "running", "results": results}
    asyncio.create_task(run())
    return {"crawl_id": crawl_id, "status": "running"}

@router.get("/crawl/{crawl_id}")
async def get_crawl_status(crawl_id: str):
    data = _active.get(crawl_id)
    if not data:
        raise HTTPException(404, "Crawl not found")
    return data
