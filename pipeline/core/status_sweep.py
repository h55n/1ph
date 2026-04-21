"""
status_sweep.py — Runs after every pipeline upsert.
Recalculates status for every active hackathon based on today's date.
Also checks URL health and increments url_health_fails.
"""
from datetime import date, datetime, timezone
import httpx


def _today() -> date:
    return datetime.now(timezone.utc).date()


def calculate_status(reg_close_str: str, reg_open_str: str = None) -> str:
    """
    Pure function — given date strings, returns the correct HackStatus.
    """
    today = _today()
    try:
        reg_close = date.fromisoformat(reg_close_str[:10])
    except (ValueError, TypeError):
        return "OPEN"

    if today > reg_close:
        return "CLOSED"
    if (reg_close - today).days <= 7:
        return "CLOSING_SOON"

    if reg_open_str:
        try:
            reg_open = date.fromisoformat(reg_open_str[:10])
            if today < reg_open:
                return "UPCOMING"
        except (ValueError, TypeError):
            pass

    return "OPEN"


def _check_url_health(url: str) -> bool:
    """Returns True if URL is alive (2xx/3xx), False otherwise."""
    try:
        with httpx.Client(timeout=10, follow_redirects=True) as client:
            r = client.head(url, headers={"User-Agent": "1ph-bot/1.0"})
            if r.status_code < 400:
                return True
            r2 = client.get(url, headers={"User-Agent": "1ph-bot/1.0"})
            return r2.status_code < 400
    except Exception:
        return False


def run_sweep(supabase_client) -> dict:
    """
    Fetches all non-CLOSED hackathons, recalculates their status,
    checks URL health, and bulk-updates the DB.

    Returns a summary dict.
    """
    summary = {"updated": 0, "closed": 0, "url_flagged": 0, "errors": 0, "deleted": 0}

    try:
        # Fetch all active hackathons
        response = supabase_client.table("Hackathon").select(
            "id, registrationClose, registrationOpen, status, applyUrl, urlHealthFails"
        ).neq("status", "CLOSED").execute()

        rows = response.data or []
    except Exception as e:
        print(f"[status_sweep] Failed to fetch rows: {e}")
        summary["errors"] += 1
        return summary

    updates = []
    url_updates = []

    for row in rows:
        try:
            new_status = calculate_status(
                row.get("registrationClose", ""),
                row.get("registrationOpen"),
            )

            update = {"id": row["id"], "status": new_status}

            # URL health check for active hackathons
            current_fails = row.get("urlHealthFails") or 0
            url = row.get("applyUrl", "")

            if url and new_status != "CLOSED":
                alive = _check_url_health(url)
                if not alive:
                    new_fails = current_fails + 1
                    update["urlHealthFails"] = new_fails
                    if new_fails >= 7:
                        update["status"] = "CLOSED"
                        summary["url_flagged"] += 1
                        summary["closed"] += 1
                    else:
                        summary["url_flagged"] += 1
                else:
                    if current_fails > 0:
                        update["urlHealthFails"] = 0  # reset on success

            if new_status == "CLOSED" and row.get("status") != "CLOSED":
                summary["closed"] += 1

            updates.append(update)

        except Exception as e:
            print(f"[status_sweep] Error processing row {row.get('id')}: {e}")
            summary["errors"] += 1

    # Batch update in chunks of 50
    chunk_size = 50
    for i in range(0, len(updates), chunk_size):
        chunk = updates[i : i + chunk_size]
        try:
            for record in chunk:
                rid = record.pop("id")
                supabase_client.table("Hackathon").update(record).eq("id", rid).execute()
                record["id"] = rid  # restore for logging
            summary["updated"] += len(chunk)
        except Exception as e:
            print(f"[status_sweep] Batch update error: {e}")
            summary["errors"] += 1

    # Delete hackathons closed for more than 7 days
    from datetime import timedelta
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    try:
        supabase_client.table("Hackathon").delete().eq("status", "CLOSED").lt("registrationClose", cutoff).execute()
        print(f"[status_sweep] Deleted hackathons closed before {cutoff[:10]}")
    except Exception as e:
        print(f"[status_sweep] Deletion error: {e}")
        summary["errors"] += 1

    return summary
