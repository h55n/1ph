"""ZeroCrawl — Job Manager."""
from __future__ import annotations
import json, uuid
from datetime import datetime, timezone
from typing import Optional
from loguru import logger
from ..models import BatchJob, JobStatus, ScrapeResult
from .cache import get_url_fingerprint
from .db import DB, init_db

class JobManager:
    @staticmethod
    async def create_batch_job(urls, config=None, webhook_url=None, webhook_secret=None):
        await init_db()
        job_id = str(uuid.uuid4())
        config = config or {}
        async with DB() as db:
            await db.execute(
                "INSERT INTO jobs (id,type,status,config,webhook_url,webhook_secret,created_at) VALUES (?,?,?,?,?,?,?)",
                (job_id,"batch","queued",json.dumps(config),webhook_url,webhook_secret,datetime.now(timezone.utc).replace(tzinfo=None).isoformat()),
            )
            rows = [(str(uuid.uuid4()),job_id,url,get_url_fingerprint(url),"queued",datetime.now(timezone.utc).replace(tzinfo=None).isoformat()) for url in urls]
            await db.executemany(
                "INSERT OR IGNORE INTO requests (id,job_id,url,url_fingerprint,status,queued_at) VALUES (?,?,?,?,?,?)", rows
            )
            await db.commit()
        return BatchJob(id=job_id, urls=urls, status="queued")

    @staticmethod
    async def get_status(job_id: str) -> JobStatus:
        async with DB() as db:
            job = await db.fetchone("SELECT * FROM jobs WHERE id=?", (job_id,))
            if not job:
                raise ValueError(f"Job {job_id} not found")
            counts = await db.fetchone(
                "SELECT COUNT(*) AS total, SUM(CASE WHEN status='done' THEN 1 ELSE 0 END) AS completed, SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) AS failed, SUM(CASE WHEN status='skipped' THEN 1 ELSE 0 END) AS skipped FROM requests WHERE job_id=?",
                (job_id,),
            )
            return JobStatus(
                id=job_id, type=job["type"], status=job["status"],
                total=counts["total"] or 0, completed=counts["completed"] or 0,
                failed=counts["failed"] or 0, skipped=counts["skipped"] or 0,
                created_at=datetime.fromisoformat(job["created_at"]) if job["created_at"] else None,
                started_at=datetime.fromisoformat(job["started_at"]) if job["started_at"] else None,
                completed_at=datetime.fromisoformat(job["completed_at"]) if job["completed_at"] else None,
            )

    @staticmethod
    async def get_results(job_id: str, limit: int = 1000, offset: int = 0) -> list[ScrapeResult]:
        async with DB() as db:
            rows = await db.fetchall("SELECT result FROM results WHERE job_id=? ORDER BY created_at LIMIT ? OFFSET ?", (job_id,limit,offset))
        results = []
        for row in rows:
            try:
                results.append(ScrapeResult(**json.loads(row["result"])))
            except Exception as e:
                logger.debug(f"Deserialise error: {e}")
        return results

    @staticmethod
    async def store_result(job_id, request_id, result: ScrapeResult):
        result_id = str(uuid.uuid4())
        async with DB() as db:
            await db.execute(
                "INSERT INTO results (id,job_id,request_id,url,result,created_at) VALUES (?,?,?,?,?,?)",
                (result_id,job_id,request_id,result.url,result.model_dump_json(),datetime.now(timezone.utc).replace(tzinfo=None).isoformat()),
            )
            status = "done" if result.status != "failed" else "failed"
            await db.execute("UPDATE requests SET status=?,result_id=?,processed_at=? WHERE id=?", (status,result_id,datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),request_id))
            await db.commit()
        await JobManager._update_job_stats(job_id)

    @staticmethod
    async def _update_job_stats(job_id):
        async with DB() as db:
            counts = await db.fetchone(
                "SELECT COUNT(*) AS total, SUM(CASE WHEN status IN ('done','failed','skipped') THEN 1 ELSE 0 END) AS processed FROM requests WHERE job_id=?", (job_id,)
            )
            if counts:
                total, processed = counts["total"] or 0, counts["processed"] or 0
                new_status = "completed" if processed >= total > 0 else "running"
                await db.execute("UPDATE jobs SET status=? WHERE id=?", (new_status, job_id))
                if new_status == "completed":
                    await db.execute("UPDATE jobs SET completed_at=? WHERE id=?", (datetime.now(timezone.utc).replace(tzinfo=None).isoformat(), job_id))
                await db.commit()

    @staticmethod
    async def get_pending_requests(job_id, limit=10):
        async with DB() as db:
            return await db.fetchall("SELECT * FROM requests WHERE job_id=? AND status='queued' ORDER BY priority DESC LIMIT ?", (job_id,limit))

    @staticmethod
    async def mark_request_processing(request_id):
        async with DB() as db:
            await db.execute("UPDATE requests SET status='processing' WHERE id=?", (request_id,))
            await db.commit()

    @staticmethod
    async def mark_request_failed(request_id, error):
        async with DB() as db:
            await db.execute("UPDATE requests SET status='failed',error=?,processed_at=? WHERE id=?", (error,datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),request_id))
            await db.commit()

    @staticmethod
    async def cancel_job(job_id):
        async with DB() as db:
            await db.execute("UPDATE jobs SET status='cancelled' WHERE id=?", (job_id,))
            await db.execute("UPDATE requests SET status='skipped' WHERE job_id=? AND status='queued'", (job_id,))
            await db.commit()
