"""
db/client.py — PostgreSQL client wrapper using psycopg2.
All DB access goes through here. Handles upserts, dedup checks, run logging.
"""
import os
import uuid
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise EnvironmentError("DATABASE_URL must be set in .env")
    return psycopg2.connect(db_url)

def get_existing_ids(source: str) -> set[str]:
    ids = set()
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT "sourceId" FROM "Hackathon" WHERE source = %s AND "sourceId" IS NOT NULL', (source,))
                for row in cur.fetchall():
                    ids.add(row[0])
    except Exception as e:
        print(f"[db] Failed to fetch existing IDs for {source}: {e}")
    return ids

def to_camel_case(snake_str: str) -> str:
    components = snake_str.split('_')
    return components[0] + "".join(x.title() for x in components[1:])

def upsert_hackathons(records: list[dict], source: str) -> dict:
    existing_ids = get_existing_ids(source)
    inserted = 0
    updated = 0
    errors = 0
    now = datetime.now(timezone.utc).isoformat()

    for raw_record in records:
        record = {to_camel_case(k): v for k, v in raw_record.items() if v is not None}
        record["source"] = source
        record["lastSyncedAt"] = now
        record["updatedAt"] = now

        source_id = record.get("sourceId")
        is_update = source_id and source_id in existing_ids

        if is_update:
            update_fields = {k: v for k, v in record.items() if k not in ("id", "createdAt", "isVerified", "isFeatured", "slug")}
            keys = list(update_fields.keys())
            values = list(update_fields.values())
            set_clause = ", ".join([f'"{k}" = %s' for k in keys])
            query = f'UPDATE "Hackathon" SET {set_clause} WHERE source = %s AND "sourceId" = %s'
            params = values + [source, source_id]
            try:
                with get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute(query, params)
                    conn.commit()
                updated += 1
            except Exception as e:
                print(f"[db] Update error: {e}")
                errors += 1
        else:
            if "id" not in record:
                record["id"] = str(uuid.uuid4())
            keys = list(record.keys())
            values = list(record.values())
            columns = ", ".join([f'"{k}"' for k in keys])
            placeholders = ", ".join(["%s"] * len(values))
            query = f'INSERT INTO "Hackathon" ({columns}) VALUES ({placeholders})'
            try:
                with get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute(query, values)
                    conn.commit()
                inserted += 1
                if source_id:
                    existing_ids.add(source_id)
            except Exception as e:
                err_str = str(e)
                if "slug" in err_str and "unique" in err_str.lower():
                    record["slug"] = f"{record['slug']}-{str(uuid.uuid4())[:4]}"
                    values = list(record.values())
                    try:
                        with get_connection() as conn:
                            with conn.cursor() as cur:
                                cur.execute(query, values)
                            conn.commit()
                        inserted += 1
                    except:
                        errors += 1
                else:
                    errors += 1
    return {"inserted": inserted, "updated": updated, "errors": errors}

def log_pipeline_run(source: str, status: str, new_count: int, updated_count: int, closed_count: int = 0, error_log: str = None):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'INSERT INTO "PipelineRun" (id, source, "runAt", status, "newCount", "updatedCount", "closedCount", "errorLog") VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                    (str(uuid.uuid4()), source, datetime.now(timezone.utc).isoformat(), status, new_count, updated_count, closed_count, error_log)
                )
            conn.commit()
    except Exception as e:
        print(f"[db] Failed to log pipeline run: {e}")

# Provide dummy get_client() for run.py which calls it
def get_client():
    return None
