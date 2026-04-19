"""
db/client.py — Supabase client wrapper.
All DB access goes through here. Handles upserts, dedup checks, run logging.
"""
import os
from datetime import datetime, timezone
from typing import Optional

from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_client: Optional[Client] = None


def get_client() -> Client:
    global _client
    if _client is None:
        url = os.environ.get("SUPABASE_URL", "").strip()
        key = os.environ.get("SUPABASE_SERVICE_KEY", "").strip()
        if not url or not key:
            raise EnvironmentError(
                "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set. "
                "Copy pipeline/.env.example to pipeline/.env and fill them in."
            )
        _client = create_client(url, key)
    return _client


def get_existing_ids(source: str) -> set[str]:
    """
    Returns a set of source_ids already in the DB for this source.
    Used for dedup — if source_id exists, we UPDATE instead of INSERT.
    """
    client = get_client()
    try:
        response = client.table("Hackathon").select("sourceId").eq("source", source).execute()
        return {row["sourceId"] for row in (response.data or []) if row.get("sourceId")}
    except Exception as e:
        print(f"[db] Failed to fetch existing IDs for {source}: {e}")
        return set()


def upsert_hackathons(records: list[dict], source: str) -> dict:
    """
    Upserts a list of normalised hackathon dicts.
    Uses (source, source_id) as the conflict key — safe to re-run anytime.

    Returns summary: {inserted, updated, errors}
    """
    client = get_client()
    existing_ids = get_existing_ids(source)

    inserted = 0
    updated = 0
    errors = 0
    now = datetime.now(timezone.utc).isoformat()

    for record in records:
        # Stamp the source correctly
        record["source"] = source
        record["last_synced_at"] = now
        record["updated_at"] = now

        source_id = record.get("source_id")
        is_update = source_id and source_id in existing_ids

        try:
            if is_update:
                # UPDATE — preserve created_at, id, is_verified, is_featured set by admin
                update_fields = {k: v for k, v in record.items() if k not in (
                    "id", "created_at", "is_verified", "is_featured", "slug"
                )}
                client.table("Hackathon").update(update_fields).eq("source", source).eq("sourceId", source_id).execute()
                updated += 1
            else:
                # INSERT — full record
                client.table("Hackathon").insert(record).execute()
                inserted += 1
                if source_id:
                    existing_ids.add(source_id)
        except Exception as e:
            err_str = str(e)
            # Unique slug conflict → regenerate slug and retry once
            if "slug" in err_str and "unique" in err_str.lower():
                try:
                    import uuid
                    record["slug"] = f"{record['slug']}-{str(uuid.uuid4())[:4]}"
                    client.table("Hackathon").insert(record).execute()
                    inserted += 1
                except Exception:
                    errors += 1
            else:
                print(f"[db] Upsert error for '{record.get('title', '?')}': {err_str[:120]}")
                errors += 1

    return {"inserted": inserted, "updated": updated, "errors": errors}


def log_pipeline_run(
    source: str,
    status: str,
    new_count: int,
    updated_count: int,
    closed_count: int = 0,
    error_log: Optional[str] = None,
) -> None:
    """Writes one row to the pipeline_runs table."""
    client = get_client()
    try:
        client.table("PipelineRun").insert({
            "source": source,
            "run_at": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "new_count": new_count,
            "updated_count": updated_count,
            "closed_count": closed_count,
            "error_log": error_log,
        }).execute()
    except Exception as e:
        # Never let logging crash the pipeline
        print(f"[db] Failed to log pipeline run for {source}: {e}")
