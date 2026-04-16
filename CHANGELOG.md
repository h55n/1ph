# CHANGELOG.md

## [Unreleased]

### Changed
- Pipeline execution fully migrated to GitHub Actions; Railway runtime is no longer part of the deploy path.
- Prisma schema source of truth consolidated to `packages/db/schema.prisma` for all workspaces.
- Pipeline workflow updated with bounded runtime and Puppeteer/Chrome CI optimization.

## [0.1.0] — 2026-04-14
### Added
- Initial scaffold and project documentation
- BRD v1.1.0 — all decisions resolved
- MASTER_PROMPT.md for coding agent
- Prisma schema (complete data model)
- Full task breakdown (TASK_001 through TASK_007)
- Risk register, architecture doc, onboarding guide
