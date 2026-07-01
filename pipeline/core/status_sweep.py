"""
status_sweep.py — Runs after every pipeline upsert.
Recalculates status for every active hackathon based on today's date.
Also checks URL health and increments url_health_fails.
"""
from datetime import date, datetime, timezone
import httpx
from psycopg2.extras import DictCursor

from pipeline.db.client import get_connection

def _today() -> date:
    return datetime.now(timezone.utc).date()

def calculate_status(reg_close_str: str, reg_open_str: str = None) -> str:
    today = _today()
    try:
        reg_close = date.fromisoformat(str(reg_close_str)[:10])
    except (ValueError, TypeError):
        return "OPEN"

    if today > reg_close:
        return "CLOSED"
    if (reg_close - today).days <= 7:
        return "CLOSING_SOON"

    if reg_open_str:
        try:
            reg_open = date.fromisoformat(str(reg_open_str)[:10])
            if today < reg_open:
                return "UPCOMING"
        except (ValueError, TypeError):
            pass

    return "OPEN"

def _check_url_health(url: str) -> bool:
    try:
        with httpx.Client(timeout=10, follow_redirects=True) as client:
            r = client.head(url, headers={"User-Agent": "1ph-bot/1.0"})
            if r.status_code < 400:
                return True
            r2 = client.get(url, headers={"User-Agent": "1ph-bot/1.0"})
            return r2.status_code < 400
    except Exception:
        return False

def run_sweep(client) -> dict:
    summary = {"updated": 0, "closed": 0, "url_flagged": 0, "errors": 0, "deleted": 0}

    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute('SELECT id, "registrationClose", "registrationOpen", status, "applyUrl", "urlHealthFails" FROM "Hackathon"')
                rows = [dict(r) for r in cur.fetchall()]
    except Exception as e:
        print(f"[status_sweep] Failed to fetch rows: {e}")
        summary["errors"] += 1
        return summary

    updates = []

    for row in rows:
        try:
            new_status = calculate_status(
                row.get("registrationClose", ""),
                row.get("registrationOpen"),
            )

            if new_status != row.get("status"):
                update = {"id": row["id"], "status": new_status}
                if new_status == "CLOSED":
                    summary["closed"] += 1
                updates.append(update)

            current_fails = row.get("urlHealthFails") or 0
            url = row.get("applyUrl", "")
            
            effective_status = new_status if any(u.get("id") == row["id"] for u in updates) else row.get("status")

            if url and effective_status != "CLOSED":
                alive = _check_url_health(url)
                if not alive:
                    new_fails = current_fails + 1
                    existing_update = next((u for u in updates if u["id"] == row["id"]), None)
                    if existing_update:
                        existing_update["urlHealthFails"] = new_fails
                        if new_fails >= 7:
                            existing_update["status"] = "CLOSED"
                            summary["closed"] += 1
                    else:
                        updates.append({"id": row["id"], "urlHealthFails": new_fails})
                    summary["url_flagged"] += 1
                else:
                    if current_fails > 0:
                        existing_update = next((u for u in updates if u["id"] == row["id"]), None)
                        if existing_update:
                            existing_update["urlHealthFails"] = 0
                        else:
                            updates.append({"id": row["id"], "urlHealthFails": 0})
        except Exception as e:
            print(f"[status_sweep] Error processing row {row.get('id')}: {e}")
            summary["errors"] += 1

    chunk_size = 50
    for i in range(0, len(updates), chunk_size):
        chunk = updates[i : i + chunk_size]
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    for record in chunk:
                        rid = record.pop("id")
                        keys = list(record.keys())
                        values = list(record.values())
                        set_clause = ", ".join([f'"{k}" = %s' for k in keys])
                        query = f'UPDATE "Hackathon" SET {set_clause} WHERE id = %s'
                        params = values + [rid]
                        cur.execute(query, params)
                        record["id"] = rid
                conn.commit()
            summary["updated"] += len(chunk)
        except Exception as e:
            print(f"[status_sweep] Batch update error: {e}")
            summary["errors"] += 1

    from datetime import timedelta
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('DELETE FROM "Hackathon" WHERE status = %s AND "registrationClose" < %s', ('CLOSED', cutoff))
                deleted_count = cur.rowcount
            conn.commit()
        summary["deleted"] = deleted_count
        print(f"[status_sweep] Deleted {deleted_count} CLOSED hackathons with deadline before {cutoff[:10]}")
    except Exception as e:
        print(f"[status_sweep] Deletion error: {e}")
        summary["errors"] += 1

    return summary
