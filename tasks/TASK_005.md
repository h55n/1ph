# TASK_005 — Pipeline Service (All Connectors)

**Phase:** 5  
**Estimated time:** 8–12 hours (most complex task)  
**Done when:** Daily pipeline runs, all 10 connectors fetch data, quality gate works, DB is populated

---

## Setup

### 5.1 — Pipeline Scaffold
`apps/pipeline/`
```bash
npm init -y
npm install bullmq ioredis puppeteer axios cheerio prisma @prisma/client dotenv
npm install -D typescript @types/node ts-node
```

### 5.2 — IConnector Interface
`apps/pipeline/connectors/base.ts`
```typescript
export interface RawHackathon {
  sourceId: string;
  title: string;
  organizerName: string;
  applyUrl: string;
  registrationClose: string; // ISO string
  registrationOpen?: string;
  eventStart?: string;
  eventEnd?: string;
  description?: string;
  mode?: 'ONLINE' | 'OFFLINE' | 'HYBRID';
  entryFee?: number;
  teamSizeMin?: number;
  teamSizeMax?: number;
  eligibility?: 'STUDENTS' | 'OPEN' | 'PROFESSIONALS';
  prizePool?: number;
  prizeDescription?: string;
  themeTags?: string[];
  sponsors?: string[];
  organizerLogoUrl?: string;
  scope?: 'GLOBAL' | 'INDIA';
  indiaRegion?: string;
}

export interface IConnector {
  source: string;
  fetch(): Promise<RawHackathon[]>;
}
```

---

## Connectors (build in this order — simpler first)

### 5.3 — MLH Connector
`apps/pipeline/connectors/mlh.ts`
- URL: https://mlh.io/seasons/2026/events
- Method: Axios + Cheerio (static HTML)
- Extract: event cards with title, date, location, apply link
- Scope: GLOBAL

### 5.4 — DoraHacks Connector
`apps/pipeline/connectors/dorahacks.ts`
- URL: https://dorahacks.io/api/hackathon/list?limit=50&status=open
- Method: REST API (check current endpoint in their docs)
- Extract: all open + upcoming hackathons
- Scope: GLOBAL

### 5.5 — HackerEarth Connector
`apps/pipeline/connectors/hackerearth.ts`
- URL: https://www.hackerearth.com/api/v2/challenges/
- Method: REST API
- Filter: type=hackathon only
- Scope: GLOBAL + INDIA

### 5.6 — Devfolio Connector
`apps/pipeline/connectors/devfolio.ts`
- Endpoint: https://api.devfolio.co/api/search/hackathons (GraphQL or REST)
- Method: GraphQL query or REST
- Scope: INDIA

### 5.7 — Startup India Connector
`apps/pipeline/connectors/startup-india.ts`
- URL: https://www.startupindia.gov.in/content/sih/en/innov8/challenges.html
- Also: Smart India Hackathon page
- Method: Axios + Cheerio
- Scope: INDIA

### 5.8 — Hack2Skill Connector
`apps/pipeline/connectors/hack2skill.ts`
- URL: https://hack2skill.com/hackathons
- Method: Axios + Cheerio (may need Puppeteer if JS-rendered)
- Scope: INDIA

### 5.9 — Toplang Connector
`apps/pipeline/connectors/toplang.ts`
- URL: https://toplang.io/hackathons (verify current URL)
- Method: Axios + Cheerio
- Scope: INDIA

### 5.10 — HackerRank Connector
`apps/pipeline/connectors/hackerrank.ts`
- URL: https://www.hackerrank.com/contests (filter hackathon type)
- Method: Puppeteer (JS-rendered)
- Only include contests tagged as hackathon/build
- Scope: GLOBAL

### 5.11 — Unstop Connector
`apps/pipeline/connectors/unstop.ts`
- URL: https://unstop.com/hackathons
- Method: Puppeteer (JS-rendered, heavy)
- Filter to hackathons/build-a-thons — exclude case studies, quizzes, debates
- Add 3s delay between page requests
- Scope: INDIA
- ⚠️ Most likely to get blocked — build last, handle PARTIAL gracefully

### 5.12 — Devpost Connector
`apps/pipeline/connectors/devpost.ts`
- URL: https://devpost.com/hackathons?sort_by=Upcoming
- Method: Puppeteer (JS-rendered)
- Paginate through results (default 24/page)
- Add 2s delay between page requests
- Scope: GLOBAL
- ⚠️ Rate limiting possible — catch errors, return partial results as PARTIAL not FAILED

---

## Pipeline Core

### 5.13 — Normalizer
`apps/pipeline/normalizer/index.ts`
- Maps RawHackathon → Hackathon Prisma model fields
- Normalizes dates to DateTime
- Generates slug from title (kebab-case, unique)
- Infers scope from indiaRegion or organizerName if not provided

### 5.14 — Quality Gate
`apps/pipeline/quality-gate/index.ts`

Runs in order:
1. `checkRequiredFields()` — title, applyUrl, registrationClose, organizerName
2. `checkUrlHealth()` — HEAD request to applyUrl, must return 2xx
3. `checkKeywordBlocklist()` — title.toLowerCase() must NOT contain:
   ["quiz", "case study", "debate", "trivia", "essay contest", "moot court", "management competition"]
4. `checkDuplicate()` — query DB for same source+sourceId; fuzzy title match if no sourceId
5. `checkSponsorForCollege()` — if organizerName contains college/university keywords AND sponsors is empty → FAIL

### 5.15 — Tier Engine
`apps/pipeline/tier-engine/index.ts` + `t1-orgs.ts`

```typescript
// t1-orgs.ts — SINGLE SOURCE OF TRUTH
export const T1_ORGS = [
  // Global
  'google', 'meta', 'microsoft', 'amazon', 'github', 'nasa', 'openai',
  'anthropic', 'goldman sachs', 'jpmorgan', 'ethereum foundation',
  // India
  'flipkart', 'walmart global tech', 'nasscom', 'startup india', 'dpiit',
  'isro', 'nic', 'smart india hackathon', 'sih',
  // IIT nationals — match "iit" + national/national-level
];
```

### 5.16 — Status Sweep
`apps/pipeline/status-sweep/index.ts`
- Runs after all connectors complete
- Updates status for all hackathons based on today's date
- Increments urlHealthFails for hackathons with dead URLs
- Auto-marks CLOSED if urlHealthFails >= 7

### 5.17 — Scheduler
`apps/pipeline/scheduler/cron.ts`
- BullMQ queue: 'pipeline'
- One job per source connector
- Concurrency: 3 (don't hammer all sources simultaneously)
- Express.js POST /trigger endpoint (called by GitHub Actions)

### 5.18 — GitHub Actions Cron
`.github/workflows/pipeline-trigger.yml`
```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # 02:00 UTC daily
  workflow_dispatch:      # manual trigger

jobs:
  trigger:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger pipeline
        run: |
          curl -X POST ${{ secrets.PIPELINE_WEBHOOK_URL }} \
            -H "Authorization: Bearer ${{ secrets.PIPELINE_WEBHOOK_SECRET }}"
```

---

## Definition of Done
- [ ] IConnector interface implemented
- [ ] All 10 source connectors fetch data without crashing
- [ ] Normalizer maps all sources to Hackathon model
- [ ] Quality gate rejects: no dates, dead URLs, keyword matches, unsponsored college
- [ ] Tier engine assigns T1/T2/T3 correctly
- [ ] Status sweep updates all statuses daily
- [ ] pipeline_run record written after each source run
- [ ] GitHub Actions cron triggers pipeline at 02:00 UTC
- [ ] Devpost + Unstop handle rate limiting gracefully (PARTIAL, not crash)
