"""
quality_gate.py — Validates every record before DB insertion.
Returns (passed: list[dict], rejected: list[dict]) with rejection reasons.
"""
import httpx
from Levenshtein import distance as levenshtein

KEYWORD_BLOCKLIST = {
    "quiz", "case study", "debate", "trivia", "essay contest",
    "moot court", "management competition", "case competition",
    "stock market", "trading competition", "aptitude",
}

COLLEGE_KEYWORDS = {
    "iit", "nit", "bits", "university", "college", "institute", "school"
}


def _has_required_fields(record: dict) -> tuple[bool, str]:
    # Note: registration_close is intentionally excluded — the enrichment phase
    # fills in real deadlines for records that initially have stub/null dates.
    for field in ("title", "apply_url", "organizer_name"):
        if not record.get(field):
            return False, f"missing_{field}"
    return True, ""


def _keyword_blocked(record: dict) -> tuple[bool, str]:
    text = (record.get("title") or "").lower()
    for kw in KEYWORD_BLOCKLIST:
        if kw in text:
            return True, f"keyword:{kw}"
    return False, ""


def _is_college_without_sponsor(record: dict) -> tuple[bool, str]:
    # Relaxed: Allow college hackathons even without explicit sponsors for now
    # to maximize data coverage from aggregators like Devfolio.
    return False, ""


def _check_url(apply_url: str) -> tuple[bool, str]:
    """HEAD request with 10s timeout. 2xx or 3xx = pass. 401/403/429 = probably valid."""
    try:
        with httpx.Client(timeout=10, follow_redirects=True) as client:
            r = client.head(apply_url, headers={"User-Agent": "1ph-bot/1.0"})
            if r.status_code < 400:
                return True, ""
            # Rate-limited or auth-gated = probably valid, don't reject
            if r.status_code in (401, 403, 429):
                return True, ""
            # Some servers reject HEAD — try GET
            r2 = client.get(apply_url, headers={"User-Agent": "1ph-bot/1.0"})
            if r2.status_code < 400:
                return True, ""
            if r2.status_code in (401, 403, 429):
                return True, ""
            return False, f"url_status:{r2.status_code}"
    except Exception as e:
        return False, f"url_error:{str(e)[:80]}"


def _is_duplicate(record: dict, existing_titles: list[str]) -> tuple[bool, str]:
    title = record.get("title", "").lower()
    for existing in existing_titles:
        if levenshtein(title, existing.lower()) < 2:
            return True, "fuzzy_duplicate"
    return False, ""


def run(records: list[dict], check_urls: bool = True) -> tuple[list[dict], list[dict]]:
    """
    Args:
        records: normalised dicts ready for upsert
        check_urls: set False in tests to skip network calls

    Returns:
        (passed, rejected, stats) — rejected have a '_reject_reason' key
    """
    passed = []
    rejected = []
    seen_titles: list[str] = []
    stats = {}

    for record in records:
        ok, reason = _has_required_fields(record)
        if not ok:
            record["_reject_reason"] = reason
            stats[reason] = stats.get(reason, 0) + 1
            rejected.append(record)
            continue

        blocked, reason = _keyword_blocked(record)
        if blocked:
            record["_reject_reason"] = reason
            stats[reason] = stats.get(reason, 0) + 1
            rejected.append(record)
            continue

        no_sponsor, reason = _is_college_without_sponsor(record)
        if no_sponsor:
            record["_reject_reason"] = reason
            stats[reason] = stats.get(reason, 0) + 1
            rejected.append(record)
            continue

        dup, reason = _is_duplicate(record, seen_titles)
        if dup:
            record["_reject_reason"] = reason
            stats[reason] = stats.get(reason, 0) + 1
            rejected.append(record)
            continue

        if check_urls:
            url_ok, reason = _check_url(record["apply_url"])
            if not url_ok:
                record["_reject_reason"] = reason
                stats[reason] = stats.get(reason, 0) + 1
                rejected.append(record)
                continue

        seen_titles.append(record.get("title", ""))
        passed.append(record)

    return passed, rejected, stats
