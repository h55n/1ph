from fastapi import APIRouter
from ...queue.cache import clear_cache
from ...queue.db import get_db_path

router = APIRouter(tags=["system"])

@router.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}

@router.get("/stats")
async def stats():
    from ...queue.db import DB
    try:
        async with DB() as db:
            j = await db.fetchone("SELECT COUNT(*) as c FROM jobs")
            r = await db.fetchone("SELECT COUNT(*) as c FROM requests")
            c = await db.fetchone("SELECT COUNT(*) as c FROM cache")
        return {"jobs": j["c"] if j else 0, "requests": r["c"] if r else 0,
                "cache_entries": c["c"] if c else 0, "db_path": str(get_db_path())}
    except Exception as e:
        return {"error": str(e)}

@router.get("/cache")
async def cache_info():
    from ...queue.db import DB
    async with DB() as db:
        c = await db.fetchone("SELECT COUNT(*) as c FROM cache")
    return {"cache_entries": c["c"] if c else 0}

@router.delete("/cache")
async def clear_all_cache():
    n = await clear_cache()
    return {"cleared": n}
