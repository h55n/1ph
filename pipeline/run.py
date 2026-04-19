"""
run.py — 1ph pipeline entry point.
Orchestrates all connectors → normalizer → quality gate → tier engine → DB upsert → status sweep.

Run locally:  python pipeline/run.py
Run in CI:    python pipeline/run.py  (GitHub Actions sets env vars via secrets)
"""
import sys
import os

# Allow running as `python pipeline/run.py` from repo root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.connectors import ALL_CONNECTORS
from pipeline.core.normalizer import normalize
from pipeline.core.quality_gate import run as quality_gate
from pipeline.core.tier_engine import assign_tiers
from pipeline.core.status_sweep import run_sweep
from pipeline.db.client import get_client, upsert_hackathons, log_pipeline_run
from pipeline.logger import run_logger as log


def main():
    client = get_client()  # Fails fast if env vars missing

    log.header(len(ALL_CONNECTORS))

    totals = {"inserted": 0, "updated": 0, "rejected": 0, "ok": 0, "total": len(ALL_CONNECTORS)}

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
        print(f"[debug] {source}: {len(result.records)} raw → {len(normalized)} normalized")
        passed, rejected = quality_gate(normalized, check_urls=False)
        log.gate_result(source, len(passed), len(rejected))
        totals["rejected"] += len(rejected)

        if not passed:
            log_pipeline_run(source, "PARTIAL", 0, 0, error_log="all_records_rejected")
            continue

        # ── 4. Tier Engine ────────────────────────────────────────────
        tiered = assign_tiers(passed)

        # ── 5. Upsert to DB ───────────────────────────────────────────
        db_result = upsert_hackathons(tiered, source)
        log.upsert_result(source, db_result["inserted"], db_result["updated"], db_result["errors"])

        totals["inserted"] += db_result["inserted"]
        totals["updated"] += db_result["updated"]

        # Determine final run status
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

    # ── 6. Status Sweep ───────────────────────────────────────────────
    sweep_summary = run_sweep(client)
    log.sweep_result(sweep_summary)

    log.footer(totals)


if __name__ == "__main__":
    main()
