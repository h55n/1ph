# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - 2026-04-21

### Added
- **Pipeline:** Auto-delete functionality for hackathons closed for more than 7 days added to the end of `run_sweep()` in `pipeline/core/status_sweep.py`.
- **Pipeline:** Extracted `prize_description` field from Devfolio API and passed it to `RawHackathon`.
- **Frontend/Web:** Added description preview to `HackathonCard.tsx` appearing below the title, fetching it by adding `description: true` to the Prisma select in `app/page.tsx`.
- **Frontend/Web:** Redesigned `HackathonDetailPage` to feature explicit, structured sections for Problem Statement, Logistics, Timeline, and Prizes.
- **Frontend/Web:** Sanitized `applyUrl` on the Hackathon Details page to ensure correct redirection to external sites.
- **Frontend/Web:** Created a native Submit form utilizing FormSubmit.co for direct email forwarding instead of Google Forms.
- **Frontend/Web:** Implemented a 'City' filter in `FilterBar.tsx` and modified the Prisma query logic in `page.tsx` to allow filtering hackathons by major Indian cities.
- **Pipeline:** Created `LumaConnector` in `pipeline/connectors/luma.py` using Playwright to scrape hackathons from `lu.ma`.
- **Pipeline:** Registered `LumaConnector` in `pipeline/connectors/__init__.py`.
- **Frontend/Web:** Fixed production cache issue by manually triggering ISR revalidation for `1ph.vercel.app`.
- **Documentation:** Created `VERCEL_ENV_CHECKLIST.md` at repo root containing required Vercel environment variables and common mistakes.
- **Scripts:** Added `scripts/revalidate.sh` helper script to quickly trigger ISR revalidation.

### Remaining
- **Pipeline:** Currently running the full pipeline to populate the database and fix the "No hackathons found" issue on the live site.
- **Pipeline:** Improved the `LumaConnector` to handle city-specific discovery (Bengaluru, Pune, Mumbai, etc.) since a global search is not directly accessible.
- **Pipeline:** Verify `Startup Grants India` scraper against `startupindia.gov.in` to ensure maximum coverage.
- **Frontend/Web:** Final verification of city filters and form submissions on the live production site after data ingestion.

### Changed
- **Pipeline:** Changed Devfolio apply URL construction to correctly use subdomain format (`https://{slug}.devfolio.co`).
- **Pipeline:** Improved `normalizer.py` description handling by increasing description limit to 1000 characters and long_description to 5000 characters.
- **Pipeline:** Improved Devfolio `about` field fetching to construct richer descriptions by combining tagline, description, and about fields in `pipeline/connectors/devfolio.py`.
- **Pipeline/Quality Gate:** Rate-limited (HTTP 429) and auth-gated (HTTP 401, 403) URLs from connectors are now accepted as valid instead of being rejected by `_check_url()`.
- **Frontend/Web:** Halved the ISR revalidate time in `apps/web/app/page.tsx` from 3600 to 1800 seconds.
- **Frontend/Web:** Updated the fallback text for the About section in `apps/web/app/hackathon/[slug]/page.tsx` to display a rich multiline description using metadata (mode, scope, prize, team size).
- **Frontend/Web:** Improved text splitting logic for the `aboutParagraphs` in `hackathon/[slug]/page.tsx` to split on sentences and newline characters, filtering out noise paragraphs under 20 characters length.
- **Frontend/Web:** Modified the manual revalidate API route in `apps/web/app/api/revalidate/route.ts` to invalidate the entire site using `revalidatePath('/', 'layout')`.

### Fixed
- **Pipeline:** Fixed Devfolio URLs resulting in 404s by switching from the `/hackathons/{slug}` endpoint to the `subdomain` route.
- **Frontend/Web:** Addressed ISR cache invalidation issues on Vercel deployments.
