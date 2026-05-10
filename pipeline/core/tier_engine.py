"""
tier_engine.py — Assigns T1 / T2 / T3 prestige tier to every record.
Single source of truth for tier rules. Never inline these rules elsewhere.
"""
import json
import os

_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "t1_orgs.json")

with open(_DATA_PATH) as f:
    _T1_DATA = json.load(f)

T1_GLOBAL: list[str] = [o.lower() for o in _T1_DATA.get("global", [])]
T1_INDIA: list[str] = [o.lower() for o in _T1_DATA.get("india", [])]
T1_IIT: list[str] = [o.lower() for o in _T1_DATA.get("iit_keywords", [])]

T1_PRIZE_USD = 50_000
T1_PRIZE_INR = 4_000_000   # ₹40L

T2_PRIZE_USD = 5_000
T2_PRIZE_INR = 400_000     # ₹4L


def _in_t1_list(organizer: str) -> bool:
    org = organizer.lower()
    return (
        any(t1 in org for t1 in T1_GLOBAL)
        or any(t1 in org for t1 in T1_INDIA)
        or any(iit in org for iit in T1_IIT)
    )


def _prize_gte(record: dict, usd_threshold: float, inr_threshold: float) -> bool:
    pool = record.get("prize_pool")
    if not pool:
        return False
    currency = (record.get("prize_currency") or "USD").upper()
    if currency == "INR":
        return pool >= inr_threshold
    return pool >= usd_threshold


def assign_tier(record: dict) -> dict:
    """
    Mutates record in place, sets 'prestige_tier' = 'T1' | 'T2' | 'T3'.
    Returns the same record.
    """
    org = record.get("organizer_name", "")
    sponsors = record.get("sponsors") or []
    source = record.get("source", "")

    # ── T1 ──────────────────────────────────────────────────────────
    if (
        _in_t1_list(org)
        or _prize_gte(record, T1_PRIZE_USD, T1_PRIZE_INR)
        or (source == "MLH" and any("mlh" in s.lower() for s in sponsors))
    ):
        record["prestige_tier"] = "T1"
        return record

    # ── T2 ──────────────────────────────────────────────────────────
    is_verified = record.get("is_verified", False)
    has_sponsors = bool(sponsors)

    if (
        _prize_gte(record, T2_PRIZE_USD, T2_PRIZE_INR)
        or (is_verified and has_sponsors)
        or source in ("DEVPOST", "DEVFOLIO", "DORAHACKS")
    ):
        record["prestige_tier"] = "T2"
        return record

    # ── T3 (default) ────────────────────────────────────────────────
    record["prestige_tier"] = "T3"
    return record


def assign_tiers(records: list[dict]) -> list[dict]:
    return [assign_tier(r) for r in records]
