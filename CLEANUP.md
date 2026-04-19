# CLEANUP.md — Remove Old Pipeline, Keep Frontend

Run these commands from your repo root to surgically remove the old
Node.js/BullMQ/Railway pipeline while keeping everything in apps/web intact.

## Step 1 — Delete old pipeline directories

```bash
rm -rf apps/pipeline
rm -rf packages/pipeline
rm -rf pipeline          # if it existed before
```

## Step 2 — Delete old GitHub Actions workflows (we replace them)

```bash
# Remove only the old pipeline trigger — keep ci.yml
rm -f .github/workflows/pipeline-trigger.yml
```

## Step 3 — Clean turbo.json (remove pipeline references)

Open turbo.json. If you see any task referencing "pipeline" workspace, remove it.
Your turbo.json should only reference the "web" app tasks (build, dev, lint).

## Step 4 — Clean root package.json

Remove any scripts referencing pipeline, workers, BullMQ, Redis.
Safe scripts to keep: dev, build, lint, typecheck, db:generate, db:migrate, db:push, db:studio.

## Step 5 — Clean .env.example

Remove: REDIS_URL, BULL_*, RAILWAY_*, PUPPETEER_*, PIPELINE_WEBHOOK_*
Keep: DATABASE_URL, DIRECT_URL, NEXTAUTH_*, GOOGLE_*, GITHUB_*, SUPABASE_*, REVALIDATE_*

## Step 6 — Add new pipeline

Copy the pipeline/ folder from this ZIP into your repo root.
It sits at the same level as apps/ and packages/:

```
your-repo/
├── apps/
│   └── web/           ← untouched
├── packages/
│   └── db/            ← untouched
├── pipeline/          ← NEW (from this ZIP)
│   ├── run.py
│   ├── requirements.txt
│   └── ...
└── .github/
    └── workflows/
        ├── ci.yml         ← keep existing
        └── pipeline.yml   ← NEW (from this ZIP)
```

## Step 7 — Add GitHub Secrets

In your GitHub repo → Settings → Secrets and variables → Actions:

| Secret name           | Value                                      |
|-----------------------|--------------------------------------------|
| SUPABASE_URL          | https://your-project.supabase.co           |
| SUPABASE_SERVICE_KEY  | your service_role key (NOT anon key)       |
| WEB_REVALIDATE_URL    | https://your-domain.com/api/revalidate     |
| WEB_REVALIDATE_SECRET | same value as REVALIDATE_SECRET in web env |

## Step 8 — Verify frontend still works

```bash
cd apps/web
npm run dev
```

Should start on localhost:3000 with zero errors.

## Step 9 — Test pipeline locally

```bash
cd pipeline
cp .env.example .env
# fill in SUPABASE_URL and SUPABASE_SERVICE_KEY in .env
pip install -r requirements.txt
playwright install chromium --with-deps
python run.py
```

Watch the console. Each source logs ✓ / ⚠ / ✗ with counts.
Check your Supabase dashboard — hackathons table should populate.

## Step 10 — Trigger a manual GitHub Actions run

Go to: your-repo → Actions → Daily Hackathon Pipeline → Run workflow

Monitor the run. If it passes, you're live.
