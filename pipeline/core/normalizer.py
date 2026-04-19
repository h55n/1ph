"""
normalizer.py — Maps RawHackathon → dict ready for Supabase upsert.
Generates slug, validates dates, infers missing fields.
"""
import re
import uuid
from datetime import datetime, timezone
from typing import Optional

from ..connectors.base import RawHackathon

VALID_MODES = {"ONLINE", "OFFLINE", "HYBRID"}
VALID_ELIGIBILITY = {"STUDENTS", "OPEN", "PROFESSIONALS"}
VALID_DURATION = {"HR24", "HR48", "WEEK", "MONTH", "CUSTOM"}
VALID_SCOPES = {"GLOBAL", "INDIA"}


def _slugify(text: str, uid: str) -> str:
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    slug = slug[:80]
    # Append short uid to guarantee uniqueness
    return f"{slug}-{uid[:8]}"


def _parse_date(val: Optional[str]) -> Optional[str]:
    """Return ISO date string or None."""
    if not val:
        return None
    val = str(val).strip()
    if val == "2099-12-31":
        return val

    iso_val = val.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(iso_val).date().isoformat()
    except ValueError:
        pass

    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(val, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def normalize(raw: RawHackathon) -> Optional[dict]:
    """
    Returns a dict ready for Supabase upsert, or None if critical fields missing.
    """
    if not raw.title or not raw.apply_url or not raw.organizer_name:
        return None

    uid = str(uuid.uuid4())
    slug = _slugify(raw.title, uid)

    reg_close = _parse_date(raw.registration_close)
    if not reg_close:
        return None

    mode = raw.mode.upper() if raw.mode and raw.mode.upper() in VALID_MODES else "ONLINE"
    eligibility = raw.eligibility.upper() if raw.eligibility and raw.eligibility.upper() in VALID_ELIGIBILITY else "OPEN"
    duration = raw.duration_type.upper() if raw.duration_type and raw.duration_type.upper() in VALID_DURATION else "CUSTOM"
    scope = raw.scope.upper() if raw.scope and raw.scope.upper() in VALID_SCOPES else "GLOBAL"

    now = datetime.now(timezone.utc).isoformat()

    return {
        "id": uid,
        "title": raw.title.strip()[:255],
        "slug": slug,
        "organizer_name": raw.organizer_name.strip()[:255],
        "organizer_logo_url": raw.organizer_logo_url,
        "description": (raw.description or raw.title)[:500],
        "long_description": raw.long_description,
        "theme_tags": raw.theme_tags or [],
        "mode": mode,
        "entry_fee": raw.entry_fee,
        "entry_fee_currency": raw.entry_fee_currency or "USD",
        "team_size_min": raw.team_size_min or 1,
        "team_size_max": raw.team_size_max,
        "eligibility": eligibility,
        "duration_type": duration,
        "prize_pool": raw.prize_pool,
        "prize_currency": raw.prize_currency or "USD",
        "prize_description": raw.prize_description,
        "registration_open": _parse_date(raw.registration_open),
        "registration_close": reg_close,
        "event_start": _parse_date(raw.event_start) or reg_close,
        "event_end": _parse_date(raw.event_end),
        "apply_url": raw.apply_url.strip(),
        "source": raw.__class__.__module__.split(".")[-1].upper(),  # overridden by run.py
        "source_id": raw.source_id,
        "scope": scope,
        "india_region": raw.india_region,
        "prestige_tier": "T3",  # tier engine overwrites this
        "sponsors": raw.sponsors or [],
        "status": "UPCOMING",   # status sweep overwrites this
        "is_verified": False,
        "is_featured": False,
        "url_health_fails": 0,
        "created_at": now,
        "updated_at": now,
        "last_synced_at": now,
    }
