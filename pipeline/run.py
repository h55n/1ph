"""
run.py — 1ph pipeline entry point.
Orchestrates all connectors → normalizer → quality gate → tier engine → DB upsert → static JSON export → status sweep.

Run locally:  python pipeline/run.py
Run in CI:    python pipeline/run.py  (GitHub Actions sets env vars via secrets)
"""
import sys
import os
import json
import uuid
import httpx
from datetime import datetime, timezone

# Allow running as `python pipeline/run.py` from repo root
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from pipeline.connectors import ALL_CONNECTORS
from pipeline.core.normalizer import normalize
from pipeline.core.quality_gate import run as quality_gate
from pipeline.core.tier_engine import assign_tiers
from pipeline.core.status_sweep import run_sweep
from pipeline.core.enrichment import run_enrichment
from pipeline.db.client import get_client, upsert_hackathons, log_pipeline_run
from pipeline.logger import run_logger as log


def format_for_export(records: list[dict]) -> list[dict]:
    """Format and sort hackathons for JSON export and static fallback."""
    cleaned = []
    seen_slugs = set()

    for h in records:
        slug = h.get('slug')
        if not slug or slug in seen_slugs:
            continue
        seen_slugs.add(slug)

        cleaned_tags = []
        for tag in h.get('theme_tags', []):
            if isinstance(tag, str) and not tag.startswith('{') and len(tag) < 30:
                cleaned_tags.append(tag)
        if not cleaned_tags:
            cleaned_tags = ["General", "Open"]

        item = {
            "id": h.get("id") or str(uuid.uuid4()),
            "title": h.get("title", ""),
            "slug": slug,
            "organizerName": h.get("organizer_name", "Community Organizer"),
            "organizerLogoUrl": h.get("organizer_logo_url") or None,
            "description": h.get("description", ""),
            "longDescription": h.get("long_description") or None,
            "themeTags": cleaned_tags[:5],
            "mode": h.get("mode", "ONLINE"),
            "entryFee": float(h["entry_fee"]) if h.get("entry_fee") is not None else None,
            "entryFeeCurrency": h.get("entry_fee_currency") or "USD",
            "teamSizeMin": int(h.get("team_size_min", 1)),
            "teamSizeMax": int(h["team_size_max"]) if h.get("team_size_max") else None,
            "eligibility": h.get("eligibility", "OPEN"),
            "durationType": h.get("duration_type", "WEEK"),
            "prizePool": float(h["prize_pool"]) if h.get("prize_pool") is not None else None,
            "prizeCurrency": h.get("prize_currency") or "USD",
            "prizeDescription": h.get("prize_description") or None,
            "registrationOpen": h.get("registration_open") or None,
            "registrationClose": h.get("registration_close") or None,
            "eventStart": h.get("event_start") or None,
            "eventEnd": h.get("event_end") or None,
            "applyUrl": h.get("apply_url", "https://1ph.dev"),
            "source": h.get("source", "MANUAL"),
            "sourceId": h.get("source_id") or None,
            "scope": h.get("scope", "GLOBAL"),
            "indiaRegion": h.get("india_region") or None,
            "prestigeTier": h.get("prestige_tier", "T2"),
            "sponsors": (h.get("sponsors") or [])[:4],
            "status": h.get("status", "OPEN"),
            "isVerified": bool(h.get("is_verified", False)),
            "isFeatured": bool(h.get("is_featured", False)),
            "urlHealthFails": 0,
            "createdAt": h.get("created_at") or datetime.now(timezone.utc).isoformat(),
            "updatedAt": h.get("updated_at") or datetime.now(timezone.utc).isoformat(),
            "lastSyncedAt": datetime.now(timezone.utc).isoformat(),
        }
        cleaned.append(item)

    tier_order = {"T1": 1, "T2": 2, "T3": 3}
    cleaned.sort(key=lambda x: (
        tier_order.get(x["prestigeTier"], 3),
        -(x["prizePool"] or 0)
    ))
    return cleaned


def save_curated_dataset(records: list[dict]):
    """Save curated records to data/hackathons.json and apps/web/data/hackathons.json."""
    if not records:
        print("[pipeline] Warning: No records to save to curated dataset")
        return

    formatted = format_for_export(records)
    paths = [
        os.path.join(REPO_ROOT, "data", "hackathons.json"),
        os.path.join(REPO_ROOT, "apps", "web", "data", "hackathons.json")
    ]

    for p in paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(formatted, f, indent=2, ensure_ascii=False)
        print(f"[pipeline] Saved {len(formatted)} curated hackathons to {p}")


def trigger_frontend_revalidation():
    """Trigger Vercel on-demand revalidation if credentials are configured."""
    url = os.environ.get("WEB_REVALIDATE_URL")
    secret = os.environ.get("WEB_REVALIDATE_SECRET")
    if not url or not secret:
        return

    try:
        endpoint = f"{url.rstrip('/')}/api/revalidate"
        headers = {
            "Authorization": f"Bearer {secret}",
            "Content-Type": "application/json"
        }
        with httpx.Client(timeout=15) as client:
            resp = client.post(endpoint, headers=headers)
            print(f"[pipeline] Triggered revalidation at {endpoint}: HTTP {resp.status_code}")
    except Exception as e:
        print(f"[pipeline] Revalidation ping failed: {e}")


def main():
    client = get_client()

    log.header(len(ALL_CONNECTORS))

    totals = {"inserted": 0, "updated": 0, "rejected": 0, "ok": 0, "total": len(ALL_CONNECTORS)}
    all_tiered_records = []

    for ConnectorClass in ALL_CONNECTORS:
        connector = ConnectorClass()
        source = connector.SOURCE

        log.connector_start(source)

        # ── 1. Fetch ──────────────────────────────────────────────────
        result = connector.run()  # Never raises — always returns ConnectorResult
        log.connector_done(source, len(result.records), result.status, result.error)

        if not result.records:
            log_pipeline_run(source, result.status, 0, 0, error_log=result.error)
            continue

        # ── 2. Normalize ──────────────────────────────────────────────
        normalized = []
        for raw in result.records:
            record = normalize(raw)
            if record:
                record["source"] = source  # stamp source before gate
                normalized.append(record)

        # ── 3. Quality Gate ───────────────────────────────────────────
        print(f"[debug] {source}: {len(result.records)} raw -> {len(normalized)} normalized")
        passed, rejected, stats = quality_gate(normalized, check_urls=False)
        log.gate_result(source, len(passed), len(rejected))
        if stats:
            print(f"         -> Rejection reasons: {stats}")
        totals["rejected"] += len(rejected)

        if not passed:
            log_pipeline_run(source, "PARTIAL", 0, 0, error_log="all_records_rejected")
            continue

        # ── 4. Tier Engine ────────────────────────────────────────────
        tiered = assign_tiers(passed)
        all_tiered_records.extend(tiered)

        # ── 5. Upsert to DB (Fault-Tolerant) ──────────────────────────
        db_result = upsert_hackathons(tiered, source)
        log.upsert_result(source, db_result["inserted"], db_result["updated"], db_result["errors"])

        totals["inserted"] += db_result["inserted"]
        totals["updated"] += db_result["updated"]

        if result.status == "SUCCESS" and db_result["errors"] == 0:
            run_status = "SUCCESS"
            totals["ok"] += 1
        elif db_result["inserted"] + db_result["updated"] > 0:
            run_status = "PARTIAL"
            totals["ok"] += 1
        else:
            run_status = "FAILED"

        log_pipeline_run(
            source=source,
            status=run_status,
            new_count=db_result["inserted"],
            updated_count=db_result["updated"],
            error_log=result.error,
        )

    # ── 6. Save JSON Curated Dataset (Primary/Fallback Storage) ────────
    if all_tiered_records:
        save_curated_dataset(all_tiered_records)

    # ── 7. AI Enrichment ──────────────────────────────────────────────
    print("\n" + "="*60)
    print("  PHASE 7: AI ENRICHMENT (Mistral)")
    print("="*60)
    enrich_summary = run_enrichment(client)
    print(f"  Enrichment: {enrich_summary}")

    # ── 8. Status Sweep ───────────────────────────────────────────────
    sweep_summary = run_sweep(client)
    log.sweep_result(sweep_summary)

    # ── 9. Trigger Frontend Revalidation ──────────────────────────────
    trigger_frontend_revalidation()

    log.footer(totals)


if __name__ == "__main__":
    main()
