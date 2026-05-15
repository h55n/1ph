# 1ph — One Place for Hackathons

The cleanest hackathon directory on the internet. Built with a self-running AI pipeline that finds, enriches, and categorizes hackathons so you don't have to. It's the only directory with a built-in AI enrichment loop — it finds stub listings, scrapes the actual application pages, extracts real deadlines, parses complex prize pools, and categorizes themes automatically. Run it on GitHub Actions for free, or deploy the Next.js frontend anywhere. No ads. No noise. Just hackathons worth your time.

Aggregates from Devpost, DoraHacks, HackerEarth, Luma, MLH, Unstop, Hack2Skill, and Devfolio. Switch views seamlessly — no locked-in platforms.

```bash
npm run dev
```

### Frontend (Next.js)
```bash
npm install
cp .env.example apps/web/.env.local
# Fill in Supabase + OAuth credentials
cd packages/db && npx prisma migrate dev --name init
cd ../..
npm run dev # Start exploring!
```

### Pipeline (Python AI Scraper)
The pipeline handles everything: Playwright scraping, data normalization, AI enrichment via Mistral, and database syncing.

```bash
cd pipeline
cp .env.example .env
# Fill in SUPABASE_URL, SUPABASE_SERVICE_KEY, and MISTRAL_API_KEY
pip install -r requirements.txt
playwright install chromium --with-deps
python run.py # Run the full pipeline
```

After installation:
```bash
# Set yourself as an admin in the Supabase SQL editor:
UPDATE "User" SET role = 'ADMIN' WHERE email = 'your@email.com';
```

## Getting Started
```bash
npm run dev             # Interactive Web UI — start exploring hackathons
python run.py           # Run the full aggregation and AI enrichment pipeline
./scripts/test_pipeline.sh mlh # Test a specific connector (e.g., mlh, dorahacks)
npx prisma studio       # Open the database viewer to manage listings
npx prisma db push      # Push schema changes to your database
```

📖 [Architecture & Structure →](#architecture)

## Stack & Architecture Reference

**Frontend:** Next.js 14 · Tailwind · Supabase · Prisma · NextAuth · Turborepo  
**Pipeline:** Python 3.11 · httpx · Playwright · Supabase · Mistral AI · GitHub Actions  

```
GitHub Actions (cron 02:00 UTC)
  → pipeline/run.py
      ├── 8 source connectors (httpx + Playwright)
      ├── normalizer.py
      ├── quality_gate.py  (URL check · dedup · keyword filter)
      ├── tier_engine.py   (T1 / T2 / T3)
      ├── Supabase upsert
      ├── enrichment.py    (Mistral AI extraction)
      └── status_sweep.py  (OPEN / CLOSING_SOON / CLOSED)

Next.js (Vercel)
  → reads same Supabase DB
  → SSG + ISR (revalidates on pipeline completion)
```

**Cost: $0.** GitHub Actions free tier covers daily runs. Supabase free tier handles 5K records.

## GitHub Secrets Required

| Secret | Value |
|--------|-------|
| `SUPABASE_URL` | `https://your-project.supabase.co` |
| `SUPABASE_SERVICE_KEY` | service_role key (not anon) |
| `WEB_REVALIDATE_URL` | `https://your-domain.com/api/revalidate` |
| `WEB_REVALIDATE_SECRET` | same as `REVALIDATE_SECRET` in web env |

## Structure

```
1ph/
├── apps/web/              ← Next.js frontend (Vercel)
├── packages/db/           ← Prisma schema (shared)
├── pipeline/              ← Python pipeline (GitHub Actions)
│   ├── run.py             ← Entry point
│   ├── connectors/        ← One file per source
│   ├── core/              ← normalizer, enrichment, quality_gate, tier_engine, status_sweep
│   ├── db/                ← Supabase client
│   └── logger/            ← Console output
├── .github/workflows/
│   ├── ci.yml             ← Lint + typecheck on PRs
│   └── pipeline.yml       ← Daily cron + manual trigger
└── scripts/               ← Organization scripts (db, scrapers, deploy)
```
