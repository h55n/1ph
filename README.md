# 1ph — One Place for Hackathons

The cleanest, most complete hackathon directory on the internet.
No ads. No noise. Just hackathons.

**Stack:** Next.js 14 · Tailwind CSS · Supabase · Prisma · BullMQ · Turborepo  
**Design:** #26150B bg · #91B2DD accent · DM Serif Display + JetBrains Mono

---

## What's In This ZIP

```
BRD.md              — Full product spec (read this first)
MASTER_PROMPT.md    — Paste into your coding agent to start building
ARCHITECTURE.md     — Technical decisions and system design
CLAUDE.md           — AI rules file (copy to .cursorrules for Cursor)
ONBOARDING.md       — Step-by-step setup guide
DECISIONS.md        — Log of build decisions (append as you build)
RISKS.md            — Risk register + mitigations
CHANGELOG.md        — Version history
docs/
  USER_STORIES.md   — Full user story set
  DATA_MODELS.md    — Data model reference
  API_CONTRACTS.md  — Internal API contracts
tasks/
  TASK_001.md       — Phase 1: Monorepo + DB + Auth scaffold
  TASK_002.md       — Phase 2: Directory + Cards + Filters
  TASK_003.md       — Phase 3: Detail Pages + Auth + Bookmarks
  TASK_004.md       — Phase 4: Admin Panel
  TASK_005.md       — Phase 5: Pipeline Service (all connectors)
  TASK_006.md       — Phase 6: SEO + Polish
  TASK_007.md       — Phase 7: Deploy
scripts/
  setup.sh          — First-time setup
  dev.sh            — Start dev environment
packages/db/
  schema.prisma     — Complete Prisma schema
.env.example        — All required environment variables
.github/workflows/
  ci.yml            — Lint + typecheck on PR
  pipeline-trigger.yml — Daily pipeline cron
```

## Quick Start

```bash
# 1. Unzip and enter project
unzip 1ph.zip && cd 1ph

# 2. Run setup
chmod +x scripts/setup.sh && ./scripts/setup.sh

# 3. Open MASTER_PROMPT.md — copy the block into Claude Code / Cursor / Windsurf

# 4. Start with TASK_001.md
```

## Key Concepts

- **No in-platform applications.** Every hackathon redirects to the source to apply.
- **Two runtimes.** Frontend runs on Vercel; pipeline runs as a scheduled/manual GitHub Actions workflow.
- **Quality gate.** Every hackathon passes validation before entering the DB.
- **Prestige tiers.** T1 = elite (Google, IIT nationals, etc). T2 = established. T3 = community.
- **Closed tab.** Expired hackathons stay for historical reference, hidden from default view.
- **Organizer flow v1.** Google Form → admin reviews → manual entry. No self-serve portal yet.
