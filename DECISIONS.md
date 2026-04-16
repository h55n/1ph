# DECISIONS.md — 1ph Build Decisions

Log every significant decision made during development here.
Format: Date · Decision · Why · Trade-offs

---

## Architecture Decisions

**2026-04-14 — Turborepo monorepo**
Why: apps/web and apps/pipeline share the Prisma schema. Monorepo makes this trivial.
Trade-off: Slightly more complex initial setup vs. simpler shared types.

**2026-04-14 — Pipeline as separate Railway service**
Why: Puppeteer and BullMQ workers can't run in Vercel serverless functions (memory limits, 10s timeout). Pipeline needs an always-on Node.js process.
Trade-off: Two deployments to manage vs. impossibility of running long scrapes in serverless.

**2026-04-14 — Google Form for organizer submissions (v1)**
Why: Zero build cost, full manual quality control, ships immediately.
Trade-off: Manual admin work vs. no spam risk and no self-serve portal to build.

**2026-04-14 — Closed hackathons stay in DB**
Why: Historical reference for users, edition count for prestige scoring, organizer credibility signal.
Trade-off: More records in DB vs. better data continuity.

**2026-04-14 — Postgres full-text search (v1)**
Why: Zero extra infra, sufficient for 5K records, built into Supabase.
Trade-off: Less powerful than Meilisearch vs. no extra service to manage.

**2026-04-14 — T1 org list hardcoded in t1-orgs.ts**
Why: Simple, version-controlled, reviewable on every PR, no DB complexity.
Trade-off: Manual update required when adding new T1 orgs vs. full auditability.

**2026-04-14 — SSG with ISR for directory page**
Why: Fast LCP (<1.5s), crawlable by search engines, revalidates hourly.
Trade-off: Data up to 1hr stale vs. zero server cost and excellent SEO.

---

## Connector Decisions

*(Append here as you build each connector)*

---

## UI Decisions

*(Append here as you build)*
