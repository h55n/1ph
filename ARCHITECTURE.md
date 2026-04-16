# ARCHITECTURE.md — 1ph

## System Overview

Two independent services:

```
┌─────────────────────┐         ┌──────────────────────┐
│   apps/web          │         │   apps/pipeline       │
│   Next.js 14        │         │   Node.js + BullMQ    │
│   Vercel            │         │   Railway             │
│                     │         │                       │
│  /                  │  reads  │  Devpost connector    │
│  /hackathon/[slug]  │ ──────> │  Devfolio connector   │
│  /bookmarks         │  from   │  MLH connector        │
│  /submit            │  shared │  Unstop connector     │
│  /admin             │  Supa-  │  DoraHacks connector  │
│  /login             │  base   │  HackerEarth connector│
│                     │  DB     │  Startup India        │
│  NextAuth.js        │         │  Hack2Skill           │
│  Prisma client      │         │  HackerRank           │
│  @vercel/og         │         │  Toplang              │
└─────────────────────┘         └──────────────────────┘
           │                               │
           └─────────────┬─────────────────┘
                         ▼
               ┌──────────────────┐
               │   Supabase       │
               │   PostgreSQL     │
               │   Storage        │
               └──────────────────┘
```

## Data Flow

```
GitHub Actions (daily 02:00 UTC)
  → POST /pipeline/trigger (Railway webhook)
  → BullMQ: enqueue one job per source
  → Each worker: fetch → normalize → quality gate → tier assign → upsert
  → Status sweep: recalculate all statuses
  → Log pipeline_run record
```

## Frontend Data Strategy

- Directory page (/): SSG with ISR (revalidate: 3600)
  - Generates at build time, refreshes every hour
  - Filters applied client-side via URL params + Prisma query on ISR refresh
- Detail pages (/hackathon/[slug]): SSG with generateStaticParams
  - Full list regenerated on each pipeline run via on-demand revalidation
- Bookmarks (/bookmarks): SSR — auth-gated, user-specific
- Admin (/admin): SSR — role-gated

## Pipeline Worker Interface

Every connector implements:

```typescript
interface IConnector {
  source: Source;
  fetch(): Promise<RawHackathon[]>;
}

interface RawHackathon {
  sourceId: string;
  title: string;
  organizerName: string;
  applyUrl: string;
  registrationClose: string; // ISO date string
  // ... all optional fields
}
```

## Quality Gate Pipeline

```
record
  → checkRequiredFields()     // title, applyUrl, registrationClose, organizerName
  → checkUrlHealth()          // HTTP GET applyUrl → must return 200
  → checkKeywordBlocklist()   // no quiz/case-study/debate keywords
  → checkDuplicate()          // sourceId dedup + fuzzy title match
  → checkSponsorForCollege()  // college orgs must have sponsors[]
  → PASS → normalizer → tier engine → upsert
  → FAIL → log reason → skip
```

## Prestige Tier Decision Tree

```
is organizer in t1-orgs.ts?          → T1
OR prize_pool >= $50K / ₹40L?        → T1
OR MLH source + edition >= 3?        → T1
  ↓ else
prize_pool >= $5K / ₹4L?             → T2
OR verified + has sponsors?          → T2
OR college with named corp sponsor?  → T2
  ↓ else
passes quality gate?                 → T3
```

## Key Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Monorepo | Turborepo | Shared Prisma schema between web + pipeline |
| Pipeline isolation | Separate Railway service | Pipeline can't run in serverless Vercel functions (Puppeteer, long-running jobs) |
| Auth provider | NextAuth.js | Fastest path to Google + GitHub OAuth |
| Search v1 | Postgres FTS | Zero infra cost, sufficient for 5K records |
| OG images | @vercel/og | Edge-generated, no external service |
| Cron | GitHub Actions | Free, reliable, no extra infra |
| Organizer flow v1 | Google Form | Zero build cost, full manual quality control |
