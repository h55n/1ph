# 1ph — One Place for Hackathons

The cleanest hackathon directory on the internet. No ads. No noise. Just hackathons.

**Frontend:** Next.js 14 · Tailwind · Supabase · Prisma · NextAuth · Turborepo  
**Pipeline:** Python 3.11 · httpx · Playwright · Supabase · GitHub Actions (free cron)  
**Design:** `#26150B` bg · `#91B2DD` accent · DM Serif Display + JetBrains Mono

---

## Quick Start

### Frontend

```bash
npm install
cp .env.example apps/web/.env.local
# fill in Supabase + OAuth credentials
cd packages/db && npx prisma migrate dev --name init
cd ../..
npm run dev
# → http://localhost:3000
```

### Pipeline (local test)

```bash
cd pipeline
cp .env.example .env
# fill in SUPABASE_URL and SUPABASE_SERVICE_KEY
pip install -r requirements.txt
playwright install chromium --with-deps
python run.py
```

### Test a single connector

```bash
./scripts/test_pipeline.sh mlh
./scripts/test_pipeline.sh dorahacks
./scripts/test_pipeline.sh devpost
```

---

## Architecture

```
GitHub Actions (cron 02:00 UTC)
  → pipeline/run.py
      ├── 8 source connectors (httpx + Playwright)
      ├── normalizer.py
      ├── quality_gate.py  (URL check · dedup · keyword filter)
      ├── tier_engine.py   (T1 / T2 / T3)
      ├── Supabase upsert
      └── status_sweep.py  (OPEN / CLOSING_SOON / CLOSED)

Next.js (Vercel)
  → reads same Supabase DB
  → SSG + ISR (revalidates on pipeline completion)
```

**Cost: $0.** GitHub Actions free tier covers daily runs. Supabase free tier handles 5K records.

---

## GitHub Secrets Required

| Secret | Value |
|--------|-------|
| `SUPABASE_URL` | `https://your-project.supabase.co` |
| `SUPABASE_SERVICE_KEY` | service_role key (not anon) |
| `WEB_REVALIDATE_URL` | `https://your-domain.com/api/revalidate` |
| `WEB_REVALIDATE_SECRET` | same as `REVALIDATE_SECRET` in web env |

---

## Structure

```
1ph/
├── apps/web/              ← Next.js frontend (Vercel)
├── packages/db/           ← Prisma schema (shared)
├── pipeline/              ← Python pipeline (GitHub Actions)
│   ├── run.py             ← Entry point
│   ├── connectors/        ← One file per source
│   ├── core/              ← normalizer, quality_gate, tier_engine, status_sweep
│   ├── db/                ← Supabase client
│   ├── logger/            ← Console output
│   └── data/t1_orgs.json  ← T1 org list (version-controlled)
├── .github/workflows/
│   ├── ci.yml             ← Lint + typecheck on PRs
│   └── pipeline.yml       ← Daily cron + manual trigger
└── scripts/
    ├── dev.sh             ← Start frontend dev server
    └── test_pipeline.sh   ← Test one connector at a time
```

---

## Set yourself as admin

After first login, run in Supabase SQL editor:

```sql
UPDATE "User" SET role = 'ADMIN' WHERE email = 'your@email.com';
```
