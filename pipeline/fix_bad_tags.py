"""
fix_bad_tags.py — One-time cleanup script.
Finds hackathons with raw JSON/dict theme tags and fixes them.

Run from repo root:
    cd pipeline
    python fix_bad_tags.py
"""
import os
import re
import json
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_SERVICE_KEY"]
client = create_client(url, key)


def sanitize_tag(tag: str) -> str | None:
    if not tag:
        return None
    tag = str(tag).strip()
    if tag.startswith("{") or tag.startswith("{'"):
        try:
            normalized = tag.replace("'", '"').replace("True", "true").replace("False", "false").replace("None", "null")
            parsed = json.loads(normalized)
            name = parsed.get("name") or parsed.get("label") or parsed.get("title") or ""
            return str(name).strip() or None
        except Exception:
            m = re.search(r"""['"]?name['"]?\s*:\s*['"]([^'"{}]+)['"]""", tag)
            return m.group(1).strip() if m else None
    if len(tag) > 60:
        return None
    return tag


def fix_tags(tags: list) -> list:
    result = []
    seen = set()
    for tag in (tags or []):
        clean = sanitize_tag(tag)
        if clean and clean.lower() not in seen:
            seen.add(clean.lower())
            result.append(clean)
    return result


# Fetch all hackathons
print("Fetching all hackathons...")
response = client.table("Hackathon").select("id, title, themeTags").execute()
rows = response.data or []
print(f"Found {len(rows)} hackathons")

needs_fix = []
for row in rows:
    tags = row.get("themeTags") or []
    has_bad = any(str(t).startswith("{") for t in tags)
    if has_bad:
        needs_fix.append(row)

print(f"Found {len(needs_fix)} hackathons with bad tags")

fixed = 0
errors = 0
for row in needs_fix:
    original = row["themeTags"]
    cleaned = fix_tags(original)
    print(f"  [{row['title'][:50]}]: {original} -> {cleaned}")
    try:
        client.table("Hackathon").update({"themeTags": cleaned}).eq("id", row["id"]).execute()
        fixed += 1
    except Exception as e:
        print(f"  ERROR: {e}")
        errors += 1

print(f"\nDone. Fixed {fixed}, errors {errors}")
