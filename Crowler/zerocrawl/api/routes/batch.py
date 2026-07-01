from fastapi import APIRouter, HTTPException
from ...api.schemas import BatchScrapeRequest
from ...models import ScrapeOptions
from ...queue.manager import JobManager
from ...queue.worker import AsyncWorker
import asyncio

router = APIRouter(tags=["batch"])

@router.post("/batch/scrape")
async def batch_scrape(req: BatchScrapeRequest):
    if not req.urls:
        raise HTTPException(400, "urls list is empty")
    options = ScrapeOptions(mode=req.options.mode, timeout=req.options.timeout,
                             cache_ttl=req.options.cache_ttl)
    job = await JobManager.create_batch_job(req.urls, webhook_url=req.webhook_url, webhook_secret=req.webhook_secret)
    worker = AsyncWorker(job.id, options=options, concurrency=3)
    asyncio.create_task(worker.run())
    return {"job_id": job.id, "status": "queued", "total": len(req.urls)}

@router.get("/batch/{job_id}")
async def get_batch_status(job_id: str):
    try:
        status = await JobManager.get_status(job_id)
        return status.model_dump(mode="json")
    except ValueError as e:
        raise HTTPException(404, str(e))

@router.get("/batch/{job_id}/results")
async def get_batch_results(job_id: str, limit: int = 100, offset: int = 0):
    results = await JobManager.get_results(job_id, limit=limit, offset=offset)
    return [r.model_dump(mode="json") for r in results]

@router.delete("/batch/{job_id}")
async def cancel_batch(job_id: str):
    await JobManager.cancel_job(job_id)
    return {"job_id": job_id, "status": "cancelled"}
