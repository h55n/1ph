"""ZeroCrawl — Async Worker Pool for batch jobs."""
from __future__ import annotations
import asyncio
from typing import Optional
from loguru import logger
from ..models import ScrapeOptions, ScrapeResult
from ..engine.orchestrator import get_orchestrator
from .manager import JobManager
from .cache import get_cached, set_cached

class AsyncWorker:
    def __init__(self, job_id: str, options: Optional[ScrapeOptions] = None, concurrency: int = 3):
        self.job_id = job_id
        self.options = options or ScrapeOptions()
        self.concurrency = concurrency
        self._orchestrator = get_orchestrator()
        self._cancelled = False

    async def run(self) -> None:
        semaphore = asyncio.Semaphore(self.concurrency)
        # Update job status to running
        from .db import DB
        async with DB() as db:
            from datetime import datetime
            await db.execute("UPDATE jobs SET status='running', started_at=? WHERE id=?",
                             (datetime.utcnow().isoformat(), self.job_id))
            await db.commit()

        tasks = []
        while not self._cancelled:
            pending = await JobManager.get_pending_requests(self.job_id, limit=self.concurrency * 2)
            if not pending:
                break
            for req in pending:
                task = asyncio.create_task(self._process_request(req, semaphore))
                tasks.append(task)
            if tasks:
                done, tasks_set = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
                tasks = list(tasks_set)

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        logger.info(f"Job {self.job_id} worker finished")

    async def _process_request(self, req: dict, semaphore: asyncio.Semaphore) -> None:
        async with semaphore:
            request_id = req["id"]
            url = req["url"]
            try:
                await JobManager.mark_request_processing(request_id)

                # Check cache
                cached = await get_cached(url, self.options.cache_ttl)
                if cached and not self.options.force_refresh:
                    result = cached
                else:
                    result = await self._orchestrator.scrape(url, self.options)
                    if result.status != "failed":
                        await set_cached(url, result, self.options.cache_ttl)

                await JobManager.store_result(self.job_id, request_id, result)
            except Exception as e:
                logger.error(f"Worker error for {url}: {e}")
                await JobManager.mark_request_failed(request_id, str(e))

    def cancel(self):
        self._cancelled = True
