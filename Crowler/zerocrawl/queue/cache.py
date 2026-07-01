"""ZeroCrawl — Result Cache with TTL."""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import urlparse, urlencode, parse_qs
from loguru import logger
from ..models import ScrapeResult
from .db import DB

def _fingerprint_url(url: str) -> str:
    try:
        parsed = urlparse(url.lower())
        qs = parse_qs(parsed.query)
        sorted_qs = urlencode(sorted(qs.items()), doseq=True)
        normalised = parsed._replace(query=sorted_qs, fragment="").geturl()
    except Exception:
        normalised = url
    return hashlib.sha256(normalised.encode()).hexdigest()

_mem_cache: dict[str, tuple[ScrapeResult, datetime]] = {}

async def get_cached(url: str, ttl: int = 3600) -> Optional[ScrapeResult]:
    fp = _fingerprint_url(url)
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if fp in _mem_cache:
        result, cached_at = _mem_cache[fp]
        if (now - cached_at).total_seconds() < ttl:
            return result
        del _mem_cache[fp]
    try:
        from .db import init_db, get_connection
        await init_db()
        async with await get_connection() as conn:
            cursor = await conn.execute("SELECT result, expires_at FROM cache WHERE url_fingerprint=?", (fp,))
            row = await cursor.fetchone()
            if row and row["expires_at"]:
                exp = datetime.fromisoformat(row["expires_at"])
                if now < exp:
                    import json
                    data = json.loads(row["result"])
                    return ScrapeResult(**data)
    except Exception as e:
        logger.debug(f"Cache read error: {e}")
    return None

async def set_cached(url: str, result: ScrapeResult, ttl: int = 3600) -> None:
    if ttl <= 0:
        return
    fp = _fingerprint_url(url)
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    expires_at = now + timedelta(seconds=ttl)
    _mem_cache[fp] = (result, now)
    try:
        from .db import init_db, get_connection
        await init_db()
        async with await get_connection() as conn:
            await conn.execute(
                "INSERT OR REPLACE INTO cache (url_fingerprint,result,cached_at,ttl_seconds,expires_at) VALUES (?,?,?,?,?)",
                (fp, result.model_dump_json(), now.isoformat(), ttl, expires_at.isoformat()),
            )
            await conn.commit()
    except Exception as e:
        logger.debug(f"Cache write error: {e}")

async def clear_cache(url: Optional[str] = None) -> int:
    count = 0
    if url:
        fp = _fingerprint_url(url)
        _mem_cache.pop(fp, None)
        try:
            async with DB() as db:
                cur = await db.execute("DELETE FROM cache WHERE url_fingerprint=?", (fp,))
                await db.commit()
                count = cur.rowcount
        except Exception:
            pass
    else:
        _mem_cache.clear()
        try:
            async with DB() as db:
                cur = await db.execute("DELETE FROM cache")
                await db.commit()
                count = cur.rowcount
        except Exception:
            pass
    return count

def get_url_fingerprint(url: str) -> str:
    return _fingerprint_url(url)
