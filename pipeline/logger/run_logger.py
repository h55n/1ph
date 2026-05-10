"""
run_logger.py — Console output and DB logging for every pipeline run.
Keeps the terminal readable. Never crashes the pipeline.
"""
from datetime import datetime, timezone


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M:%S")


def header(total_sources: int) -> None:
    print("\n" + "═" * 60)
    print(f"  1ph Pipeline — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Sources: {total_sources}")
    print("═" * 60)


def connector_start(source: str) -> None:
    print(f"\n[{_ts()}] ▶ {source} — fetching...")


def connector_done(source: str, count: int, status: str, error: str = None) -> None:
    icon = "✓" if status == "SUCCESS" else ("⚠" if status == "PARTIAL" else "✗")
    print(f"[{_ts()}] {icon} {source} — {count} records ({status})")
    if error:
        print(f"         ↳ {error[:120]}")


def gate_result(source: str, passed: int, rejected: int) -> None:
    print(f"         ↳ Quality gate: {passed} passed, {rejected} rejected")


def upsert_result(source: str, inserted: int, updated: int, errors: int) -> None:
    print(f"         ↳ DB: +{inserted} new, ~{updated} updated, {errors} errors")


def sweep_result(summary: dict) -> None:
    print(f"\n[{_ts()}] ↻ Status sweep — {summary.get('updated', 0)} updated, "
          f"{summary.get('closed', 0)} closed, {summary.get('url_flagged', 0)} URL flags")


def footer(totals: dict) -> None:
    print("\n" + "─" * 60)
    print(f"  Total inserted : {totals.get('inserted', 0)}")
    print(f"  Total updated  : {totals.get('updated', 0)}")
    print(f"  Total rejected : {totals.get('rejected', 0)}")
    print(f"  Sources OK     : {totals.get('ok', 0)}/{totals.get('total', 0)}")
    print("─" * 60 + "\n")
