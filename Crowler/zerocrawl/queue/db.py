"""
ZeroCrawl — Database Connection Manager
Async SQLite via aiosqlite. Handles schema init and connection pooling.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, AsyncGenerator

import aiosqlite
from loguru import logger

from ..config import settings

_SCHEMA_PATH = Path(__file__).parent / "schema.sql"
_db_path: Path | None = None
_initialized = False


def get_db_path() -> Path:
    global _db_path
    if _db_path is None:
        _db_path = settings.get_db_path()
        _db_path.parent.mkdir(parents=True, exist_ok=True)
    return _db_path


async def get_connection() -> aiosqlite.Connection:
    """Get a new aiosqlite connection (caller must close)."""
    db_path = get_db_path()
    conn = await aiosqlite.connect(str(db_path))
    conn.row_factory = aiosqlite.Row
    await conn.execute("PRAGMA journal_mode=WAL")
    await conn.execute("PRAGMA foreign_keys=ON")
    await conn.execute("PRAGMA synchronous=NORMAL")
    return conn


async def init_db() -> None:
    """Initialize the database schema (idempotent)."""
    global _initialized
    if _initialized:
        return
    schema = _SCHEMA_PATH.read_text()
    async with await get_connection() as conn:
        await conn.executescript(schema)
        await conn.commit()
    _initialized = True
    logger.debug(f"Database initialized at {get_db_path()}")


class DB:
    """Context manager for SQLite operations."""

    def __init__(self) -> None:
        self._conn: aiosqlite.Connection | None = None

    async def __aenter__(self) -> "DB":
        await init_db()
        self._conn = await get_connection()
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._conn:
            await self._conn.close()
            self._conn = None

    async def execute(self, sql: str, params: tuple = ()) -> aiosqlite.Cursor:
        assert self._conn is not None
        return await self._conn.execute(sql, params)

    async def executemany(self, sql: str, params_list: list[tuple]) -> None:
        assert self._conn is not None
        await self._conn.executemany(sql, params_list)

    async def fetchone(self, sql: str, params: tuple = ()) -> dict | None:
        assert self._conn is not None
        cursor = await self._conn.execute(sql, params)
        row = await cursor.fetchone()
        return dict(row) if row else None

    async def fetchall(self, sql: str, params: tuple = ()) -> list[dict]:
        assert self._conn is not None
        cursor = await self._conn.execute(sql, params)
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

    async def commit(self) -> None:
        assert self._conn is not None
        await self._conn.commit()

    def json_dumps(self, obj: Any) -> str:
        return json.dumps(obj, default=str)

    def json_loads(self, s: str) -> Any:
        try:
            return json.loads(s) if s else {}
        except Exception:
            return {}
