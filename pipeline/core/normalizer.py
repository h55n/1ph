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
    return f"{slug}-{uid[:8]}"


def _parse_date(val: Optional[str]) -> Optional[str]:
    """Return ISO date string or None."""
    if not val:
        return None
    val = str(val).strip()

    iso_val = f"{val[:-1]}+00:00" if val.endswith("Z") else val
    try:
        return datetime.fromisoformat(iso_val).date().isoformat()
    except ValueError:
        pass

    for fmt, slice_len in (
        ("%Y-%m-%dT%H:%M:%SZ", 20),
        ("%Y-%m-%dT%H:%M:%S", 19),
        ("%Y-%m-%d", 10),
        ("%d-%m-%Y", 10),
        ("%d/%m/%Y", 10),
        ("%m/%d/%Y", 10),
    ):
        try:
            return datetime.strptime(val[:slice_len], fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _to_timestamp(date_str: Optional[str]) -> Optional[str]:
    """Convert YYYY-MM-DD to full ISO timestamp for Postgres DateTime columns."""
    if not date_str:
        return None
    if "T" in date_str:
        return date_str
    return f"{date_str}T00:00:00+00:00"


def _sanitize_tag(tag) -> Optional[str]:
    """
    Extract a clean string from a tag that might be:
    - A plain string: "FinTech"
    - A dict: {'name': 'FinTech', 'verified': True, 'uuid': '...'}
    - A JSON-like string: "{'name': 'FinTech', ...}"
    Returns None if the tag can't be meaningfully extracted.
    """
    if tag is None:
        return None

    # Already a dict (shouldn't reach here but defensive)
    if isinstance(tag, dict):
        name = tag.get("name") or tag.get("label") or tag.get("title") or ""
        return str(name).strip() or None

    tag = str(tag).strip()
    if not tag:
        return None

    # Looks like a serialized Python dict or JSON object
    if tag.startswith("{") or tag.startswith("{'"):
        import json
        try:
            # Normalize Python dict → JSON
            normalized = tag.replace("'", '"').replace("True", "true").replace("False", "false").replace("None", "null")
            parsed = json.loads(normalized)
            name = parsed.get("name") or parsed.get("label") or parsed.get("title") or ""
            return str(name).strip() or None
        except Exception:
            # Try regex extraction
            m = re.search(r'''['"']?name['"']?\s*:\s*['"']([^'"'{}]+)['"']''', tag)
            if m:
                return m.group(1).strip()
            return None

    # Plain string — validate it's a reasonable tag (not UUID, not too long)
    if len(tag) > 60 or re.fullmatch(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', tag, re.I):
        return None

    return tag


def _sanitize_tags(tags: list) -> list[str]:
    """Sanitize a list of tags, removing bad entries."""
    result = []
    seen = set()
    for tag in (tags or []):
        clean = _sanitize_tag(tag)
        if clean and clean.lower() not in seen:
            seen.add(clean.lower())
            result.append(clean)
    return result[:8]  # cap at 8 tags


def normalize(raw: RawHackathon) -> Optional[dict]:
    """
    Returns a dict ready for Supabase upsert, or None if critical fields missing.
    """
    if not raw.title or not raw.apply_url or not raw.organizer_name:
        return None

    uid = str(uuid.uuid4())
    slug = _slugify(raw.title, uid)

    reg_close = _parse_date(raw.registration_close)
    # Allow missing registration_close, status_sweep will handle it as OPEN


    mode = raw.mode.upper() if raw.mode and raw.mode.upper() in VALID_MODES else "ONLINE"
    eligibility = raw.eligibility.upper() if raw.eligibility and raw.eligibility.upper() in VALID_ELIGIBILITY else "OPEN"
    duration = raw.duration_type.upper() if raw.duration_type and raw.duration_type.upper() in VALID_DURATION else "CUSTOM"
    scope = raw.scope.upper() if raw.scope and raw.scope.upper() in VALID_SCOPES else "GLOBAL"

    now = datetime.now(timezone.utc).isoformat()

    # Sanitize theme tags — remove raw JSON/dict objects
    clean_tags = _sanitize_tags(raw.theme_tags)

    # Automatically extract tags from title/description if they are missing
    text = (raw.title + " " + (raw.description or "")).lower()
    auto_tags = {
        "AI/ML":      ["ai", "ml", "artificial intelligence", "machine learning", "deep learning", "nlp"],
        "Web3":       ["web3", "crypto", "blockchain", "ethereum", "solana", "nft", "dao"],
        "Fintech":    ["fintech", "finance", "banking", "payment", "trading"],
        "Health":     ["health", "medtech", "healthcare", "medical", "fitness"],
        "Gaming":     ["gaming", "game", "unity", "unreal", "metaspace"],
        "Social Impact": ["social impact", "sustainability", "climate", "environment", "green"],
        "EdTech":     ["edtech", "education", "learning", "teaching", "school"],
        "Open":       ["open", "general", "any"],
        "Hardware":   ["hardware", "iot", "robotics", "embedded", "arduino", "raspberry pi"],
    }
    
    current_tags_lower = {t.lower() for t in clean_tags}
    for theme, keywords in auto_tags.items():
        if any(kw in text for kw in keywords):
            if theme.lower() not in current_tags_lower:
                clean_tags.append(theme)

    return {
        "id": uid,
        "title": raw.title.strip()[:255],
        "slug": slug,
        "organizer_name": raw.organizer_name.strip()[:255],
        "organizer_logo_url": raw.organizer_logo_url,
        "description": (raw.description or raw.title)[:1000],
        "long_description": (raw.long_description or raw.description or "")[:5000] or None,
        "theme_tags": clean_tags,
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
        "registration_open": _to_timestamp(_parse_date(raw.registration_open)),
        "registration_close": _to_timestamp(reg_close),
        "event_start": _to_timestamp(_parse_date(raw.event_start)),
        "event_end": _to_timestamp(_parse_date(raw.event_end)),
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
