"""
scripts/export_curated_hackathons.py
Pulls live hackathons from Devpost, MLH, and Devfolio,
runs normalizer, quality gate, tier engine,
and generates apps/web/lib/demo-data.ts and data/hackathons.json.
"""
import json
import os
import sys
import re
from datetime import datetime, timezone

# Add repo root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.connectors.devpost import DevpostConnector
from pipeline.connectors.mlh import MLHConnector
from pipeline.connectors.devfolio import DevfolioConnector
from pipeline.core.normalizer import normalize
from pipeline.core.quality_gate import run as quality_gate
from pipeline.core.tier_engine import assign_tiers

def main():
    print("Scraping live hackathons from Devpost, MLH, and Devfolio...")
    connectors = [DevpostConnector(), MLHConnector(), DevfolioConnector()]
    raw_all = []

    for c in connectors:
        try:
            print(f"Running connector {c.SOURCE}...")
            res = c.run()
            print(f"  -> {c.SOURCE}: {len(res.records)} records")
            # For Devfolio, limit to first 120 most recent to keep dataset balanced
            records = res.records[:120] if c.SOURCE == "DEVFOLIO" else res.records
            for r in records:
                norm = normalize(r)
                if norm:
                    norm['source'] = c.SOURCE
                    raw_all.append(norm)
        except Exception as e:
            print(f"  -> Error running {c.SOURCE}: {e}")

    print(f"Total normalized records: {len(raw_all)}")
    passed, rejected, stats = quality_gate(raw_all, check_urls=False)
    print(f"Passed quality gate: {len(passed)}, Rejected: {len(rejected)}")
    tiered = assign_tiers(passed)

    # Clean dates and ensure valid fields for TypeScript
    cleaned = []
    seen_slugs = set()
    for h in tiered:
        slug = h.get('slug')
        if not slug or slug in seen_slugs:
            continue
        seen_slugs.add(slug)

        # Ensure theme tags are valid strings (not dict representations)
        cleaned_tags = []
        for tag in h.get('theme_tags', []):
            if isinstance(tag, str) and not tag.startswith('{') and len(tag) < 30:
                cleaned_tags.append(tag)
        if not cleaned_tags:
            cleaned_tags = ["General", "Open"]

        item = {
            "id": h.get("id") or slug,
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
            "sponsors": h.get("sponsors", [])[:4],
            "status": h.get("status", "OPEN"),
            "isVerified": bool(h.get("is_verified", False)),
            "isFeatured": bool(h.get("is_featured", False)),
            "urlHealthFails": 0,
            "createdAt": h.get("created_at") or datetime.now(timezone.utc).isoformat(),
            "updatedAt": h.get("updated_at") or datetime.now(timezone.utc).isoformat(),
            "lastSyncedAt": datetime.now(timezone.utc).isoformat(),
        }
        cleaned.append(item)

    # Sort so T1 is first, followed by T2, then T3, and higher prizes first
    tier_order = {"T1": 1, "T2": 2, "T3": 3}
    cleaned.sort(key=lambda x: (
        tier_order.get(x["prestigeTier"], 3),
        -(x["prizePool"] or 0)
    ))

    print(f"Total cleaned and sorted hackathons: {len(cleaned)}")

    # Write to data/hackathons.json
    os.makedirs("data", exist_ok=True)
    with open("data/hackathons.json", "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=2)
    print("Wrote data/hackathons.json")

    # Generate apps/web/lib/demo-data.ts
    header = """// Auto-generated real hackathons cache for fallback & demo resilience
export interface DemoHackathon {
  id: string
  title: string
  slug: string
  organizerName: string
  organizerLogoUrl: string | null
  description: string
  longDescription: string | null
  themeTags: string[]
  mode: 'ONLINE' | 'OFFLINE' | 'HYBRID'
  entryFee: number | null
  entryFeeCurrency: string | null
  teamSizeMin: number
  teamSizeMax: number | null
  eligibility: 'STUDENTS' | 'OPEN' | 'PROFESSIONALS'
  durationType: 'HR24' | 'HR48' | 'WEEK' | 'MONTH' | 'CUSTOM'
  prizePool: number | null
  prizeCurrency: string | null
  prizeDescription: string | null
  registrationOpen: Date | null
  registrationClose: Date | null
  eventStart: Date | null
  eventEnd: Date | null
  applyUrl: string
  source: string
  sourceId: string | null
  scope: 'GLOBAL' | 'INDIA'
  indiaRegion: string | null
  prestigeTier: 'T1' | 'T2' | 'T3'
  sponsors: string[]
  status: 'OPEN' | 'CLOSING_SOON' | 'UPCOMING' | 'CLOSED'
  isVerified: boolean
  isFeatured: boolean
  urlHealthFails: number
  createdAt: Date
  updatedAt: Date
  lastSyncedAt: Date | null
}

const rawHackathons = """
    footer = """;

export const demoHackathons: DemoHackathon[] = rawHackathons.map((h) => ({
  ...h,
  mode: h.mode as 'ONLINE' | 'OFFLINE' | 'HYBRID',
  eligibility: h.eligibility as 'STUDENTS' | 'OPEN' | 'PROFESSIONALS',
  durationType: h.durationType as 'HR24' | 'HR48' | 'WEEK' | 'MONTH' | 'CUSTOM',
  prestigeTier: h.prestigeTier as 'T1' | 'T2' | 'T3',
  status: h.status as 'OPEN' | 'CLOSING_SOON' | 'UPCOMING' | 'CLOSED',
  scope: h.scope as 'GLOBAL' | 'INDIA',
  registrationOpen: h.registrationOpen ? new Date(h.registrationOpen) : null,
  registrationClose: h.registrationClose ? new Date(h.registrationClose) : null,
  eventStart: h.eventStart ? new Date(h.eventStart) : null,
  eventEnd: h.eventEnd ? new Date(h.eventEnd) : null,
  createdAt: new Date(h.createdAt),
  updatedAt: new Date(h.updatedAt),
  lastSyncedAt: h.lastSyncedAt ? new Date(h.lastSyncedAt) : null,
}))

export function shouldUseDemoData() {
  const url = process.env.DATABASE_URL?.trim()
  if (!url || url.includes('[SENSITIVE]')) return true
  return false
}

export function findDemoHackathon(slug: string) {
  const normalizedSlug = decodeURIComponent(slug).trim().toLowerCase()
  return demoHackathons.find((row) => row.slug.toLowerCase() === normalizedSlug)
}
"""
    with open("apps/web/lib/demo-data.ts", "w", encoding="utf-8") as f:
        f.write(header + json.dumps(cleaned, indent=2) + footer)
    print("Successfully updated apps/web/lib/demo-data.ts with live hackathons!")

if __name__ == "__main__":
    main()
