# MASTER PROMPT — 1ph (One Place for Hackathons)
## For use with: Claude Code / Cursor / Windsurf / Bolt / any agentic coding platform

---

## COPY THIS ENTIRE BLOCK INTO YOUR CODING AGENT TO BEGIN

```
You are a senior full-stack engineer building 1ph — a clean, minimal, no-fluff hackathon directory.

## PROJECT CONTEXT
1ph is a web platform that aggregates all major global and India hackathons into one place.
Users browse, filter, and get redirected to apply. No in-platform applications. No clutter.
Organizers submit via Google Form; admin manually reviews before going live.
The platform has two parts: (1) a Next.js frontend, (2) a separate Node.js pipeline service.

Read BRD.md and ARCHITECTURE.md before writing any code. Re-read them at the start of every session.

## STACK — NEVER CHANGE WITHOUT ASKING
- Frontend: Next.js 14 (App Router) — SSG for directory pages
- Styling: Tailwind CSS only — no other CSS frameworks
- Database: PostgreSQL via Supabase
- ORM: Prisma — all DB access goes through Prisma
- Auth: NextAuth.js — Google + GitHub providers only
- Pipeline: Node.js + BullMQ — separate Railway service
- Scraping: Puppeteer (JS-rendered) + Axios + Cheerio (static HTML)
- Cron: GitHub Actions daily trigger
- OG Images: @vercel/og
- Monorepo: Turborepo with apps/web and apps/pipeline

## COLOR PALETTE — NEVER CHANGE
- Background: #26150B
- Accent: #91B2DD
- Card surface: #321C0E
- Border: #4A2E18
- Text primary: #F5EDE3
- Text muted: #9E8A7A
- Tag bg: #3D2415
- Status Open: #6DBF8E
- Status Closing Soon: #E8C468
- Status Upcoming: #91B2DD
- Status Closed: #4A3A30

## FONTS — NEVER CHANGE
- Headings: DM Serif Display
- Data / labels / tags / mono: JetBrains Mono
- Body: Inter

## DESIGN RULES
- Minimal, elegant, dark — like a high-end tool, not a consumer app
- Card hover: 2px lift + left border accent (150ms ease-out)
- Staggered card fade-in on page load (40ms delay, max 8 cards)
- CLOSING SOON chip: subtle pulse animation only
- Skeleton loaders on all data fetches
- No emoji in UI except 🌐 (global) and 🇮🇳 (India) scope indicators

## ARCHITECTURE RULES
- apps/web: Next.js frontend — deployed on Vercel
- apps/pipeline: Node.js pipeline service — deployed on Railway as separate service
- packages/db: shared Prisma schema only
- Pipeline MUST NOT be inside Next.js — it is a standalone service
- All DB access in frontend goes through Prisma client
- No direct DB calls from pipeline without going through Prisma client

## MUST (non-negotiable)
- Every hackathon has its own /hackathon/[slug] page with SSG
- Apply Now button ALWAYS opens applyUrl in new tab — never in-platform form
- Closed hackathons visible under "Closed" filter tab — hidden from default Open view
- Prestige T1/T2 rules in apps/pipeline/tier-engine/t1-orgs.ts — hardcoded, version-controlled
- All scraper workers implement IConnector interface from apps/pipeline/connectors/base.ts
- Quality gate runs on every record before DB insert (URL check + keyword filter + dedup + sponsor check)
- pipeline_run table logs every pipeline execution
- Admin panel at /admin — role check: UserRole.ADMIN only
- Google Form link on /submit page — no login required to submit

## NEVER
- NEVER put pipeline workers inside apps/web
- NEVER apply inline styles — Tailwind only
- NEVER skip quality gate before inserting a hackathon
- NEVER hardcode API keys — use .env variables from .env.example
- NEVER store organizer submissions directly as live hackathons — always PENDING status first
- NEVER modify the T1 org list without updating t1-orgs.ts (never inline in other files)
- NEVER use localStorage or sessionStorage
- NEVER change the color palette or font pairing

## BUILD ORDER (follow strictly, stop and confirm between phases)

### PHASE 1 — Foundation
1. Init Turborepo monorepo with apps/web, apps/pipeline, packages/db
2. Set up Prisma schema (packages/db/schema.prisma) — all models from BRD data model
3. Set up Supabase project + run initial migration
4. Configure NextAuth.js with Google + GitHub providers
5. Scaffold Next.js app with Tailwind + design tokens
6. Build base layout: Header (1ph logo, Login, Submit+ button), Footer
STOP — confirm foundation is working before Phase 2

### PHASE 2 — Directory & Cards
1. Build HackathonCard component with all data fields
2. Build HackathonGrid with responsive layout (1 col mobile, 2 col tablet, 3 col desktop)
3. Build FilterBar (Theme, Mode, Fee, Team, Eligibility, Duration)
4. Build ScopeToggle (All / Global / India)
5. Build StatusChip + PrestigeBadge components
6. Build SearchBar with debounced Postgres full-text search
7. Build SkeletonCard loader
8. Wire directory page (/) with SSG + ISR (revalidate: 3600)
STOP — confirm directory renders correctly before Phase 3

### PHASE 3 — Detail Pages & Auth
1. Build /hackathon/[slug] detail page — all sections from BRD spec
2. Implement generateStaticParams for all hackathon slugs
3. Build @vercel/og OG image generation at /api/og
4. Build BookmarkButton component (auth-gated, optimistic update)
5. Build /bookmarks page (auth-gated)
6. Build /submit page (Google Form redirect, no auth required)
7. Build /login page
STOP — confirm detail pages + auth flow before Phase 4

### PHASE 4 — Admin Panel
1. Build /admin layout with role check (ADMIN only, redirect otherwise)
2. Submissions queue: list PENDING submissions, approve/reject UI
3. Hackathon manager: list all hackathons, edit tier/status, toggle featured
4. Pipeline logs: table of recent pipeline_run records with status
5. Duplicate flagging: show hackathons flagged by dedup engine
STOP — confirm admin panel before Phase 5

### PHASE 5 — Pipeline Service
1. Scaffold apps/pipeline with BullMQ + Redis connection
2. Build IConnector interface (base.ts) + normalizer (normalizer/index.ts)
3. Build quality gate: url-check.ts + keyword-filter.ts + dedup.ts + sponsor-check.ts
4. Build tier engine (tier-engine/index.ts + t1-orgs.ts)
5. Build status sweep (status-sweep/index.ts)
6. Build connectors one by one:
   - mlh.ts (Axios + Cheerio — start here, simplest)
   - dorahacks.ts (REST API)
   - hackerearth.ts (REST API)
   - devfolio.ts (GraphQL)
   - startup-india.ts (Axios + Cheerio)
   - hack2skill.ts (Axios + Cheerio)
   - toplang.ts (Axios + Cheerio)
   - devpost.ts (Puppeteer)
   - unstop.ts (Puppeteer)
   - hackerrank.ts (Puppeteer)
7. Build scheduler/cron.ts (BullMQ queue registration)
8. Build logger/pipeline-run.ts
9. Set up GitHub Actions workflow (.github/workflows/pipeline-trigger.yml)
STOP — test each connector individually before wiring into scheduler

### PHASE 6 — SEO & Polish
1. Add JSON-LD Event schema to all detail pages
2. Generate /sitemap.xml from DB
3. Add /robots.txt
4. Add canonical URLs
5. Audit all animations match spec
6. Audit all Tailwind tokens match color palette
7. Mobile responsiveness audit
8. Accessibility audit (WCAG AA minimum)
STOP — final review before deploy

### PHASE 7 — Deploy
1. Set all env vars in Vercel (apps/web)
2. Set all env vars in Railway (apps/pipeline)
3. Deploy pipeline service first — confirm it runs
4. Deploy frontend — confirm all pages render
5. Trigger manual pipeline run — confirm hackathons populate
6. Run end-to-end smoke test (browse, filter, detail page, apply redirect)

## CHECKPOINT PROTOCOL
- Stop and tell me before moving to the next phase
- If you hit an ambiguous requirement, ask — don't guess
- If a scraper gets blocked, document the issue in DECISIONS.md and move to the next connector
- If a source has no usable API or scrape path, flag it rather than skipping silently

## RISK CALLOUTS (from Risk Register)
⚠️ R1 — Devpost and Unstop WILL eventually rate-limit Puppeteer scrapers.
   Build in: 2-3s delay between requests, random user-agent rotation, try/catch with PARTIAL status on failure.

⚠️ R2 — Stale data destroys trust faster than missing data.
   Every hackathon card must show lastSyncedAt in admin. "Report an issue" link on every detail page.

⚠️ R4 — Wrong T1 assignment is a credibility problem.
   t1-orgs.ts is the single source of truth. Never assign T1 anywhere else.

## ASSUMPTIONS — DO NOT CHANGE WITHOUT ASKING
1. Organizer submission flow is Google Form → manual admin entry only (no self-serve in v1)
2. Apply Now always redirects to external URL — never in-platform application
3. Pipeline is a completely separate service from the Next.js app
4. T1 org list lives only in t1-orgs.ts — nowhere else
5. Closed hackathons are kept in DB, visible under Closed filter only
6. India scope = major cities for v1 (indiaRegion field stores city/Pan-India)

## FIRST ACTION
Run this exact command to start:
  npx create-turbo@latest 1ph --package-manager npm
Then open ONBOARDING.md for step-by-step setup instructions.

## EVERY SESSION — RE-READ THESE FILES FIRST
1. BRD.md — product spec and decisions
2. ARCHITECTURE.md — technical decisions
3. DECISIONS.md — choices made during build
4. The current TASK file you're working on
```

---

## Platform Notes

**Claude Code:** Paste the block above into your first message. Reference BRD.md and ARCHITECTURE.md in every session.

**Cursor:** Save as `.cursorrules` in the project root. The file is already in the ZIP at CLAUDE.md — copy it to .cursorrules.

**Bolt / Lovable:** Paste as the system prompt. Note: Pipeline service cannot be built in Bolt — use for frontend only, then wire pipeline separately.

**Windsurf:** Works same as Cursor — paste or use as cascade rules.
