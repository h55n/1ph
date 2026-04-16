# RISKS.md — 1ph Risk Register

## Active Risks

| # | Risk | Likelihood | Impact | Status |
|---|------|-----------|--------|--------|
| R1 | Devpost/Unstop block Puppeteer scrapers | High | High | Open |
| R2 | Stale data erodes user trust | Medium | High | Open |
| R3 | Google Form spam submissions | Medium | Medium | Open |
| R4 | Prestige tier misassignment | Low | High | Open |
| R5 | Apply URLs go dead post-listing | High | Low | Open |
| R6 | India regional hackathon gaps | Medium | Medium | Open |

## Mitigations

**R1 — Scraper blocking:**
- 2-3s random delay between Puppeteer requests
- Rotate user-agent strings (list in pipeline/connectors/user-agents.ts)
- Catch rate-limit errors → log as PARTIAL run, not FAILED
- Consider residential proxy service if blocking persists (Bright Data, Oxylabs)
- Cache last successful scrape; only re-fetch if >23 hours old

**R2 — Stale data:**
- `lastSyncedAt` visible in admin panel per hackathon
- "Report an issue" link on every hackathon detail page
- Admin email notification when any source returns FAILED pipeline status
- Admin flag on any hackathon where applyUrl returns non-200 for 3+ runs

**R3 — Spam submissions:**
- Google Form honeypot field (hidden field that bots fill, humans don't)
- Manual review catches all submissions before going live
- Rate: if submission volume exceeds 20/week, build self-serve portal sooner

**R4 — Tier misassignment:**
- T1 org list is version-controlled in t1-orgs.ts — reviewed on every PR
- Admin can override any tier from admin panel
- Tier assignment logged in pipeline_run for auditability

**R5 — Dead apply URLs:**
- Daily URL health check on all active hackathons
- Auto-flag if applyUrl returns non-200 for 3 consecutive runs
- Auto-CLOSED if applyUrl fails for 7 days (hackathon likely over)

**R6 — India gaps:**
- Hack2Skill + Devfolio + Unstop covers ~80% India hackathons
- Startup India covers government/DPIIT challenges
- Google Form as safety net for any missed hackathons
- Social media monitoring for #hackathon #India as v2 signal

## Critical Assumptions (must remain true)

1. Daily scraping of major sources is feasible without persistent blocks
2. Google Form + manual review sustainable under ~20 submissions/week
3. Quality gate filters >80% noise without manual review at scale
4. Users accept redirect-to-apply UX (no in-platform applications)
5. Hardcoded T1 list maintainable for v1 (<60 orgs to track)
6. Supabase free tier handles v1 data volume (~5,000 records max)

## Decision Log for Risks

If a risk materializes, document it here with date + resolution.

| Date | Risk | What Happened | Resolution |
|------|------|---------------|------------|
| — | — | — | — |
