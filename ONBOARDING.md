# ONBOARDING.md — 1ph Setup Guide

## Prerequisites

- Node.js 18+
- npm 9+
- A Supabase account (free tier works)
- A Vercel account (free tier works)
- A Railway account (free tier works for pipeline)
- Google OAuth credentials (Google Cloud Console)
- GitHub OAuth credentials (GitHub Developer Settings)

---

## Step 1 — Clone / Unzip

```bash
unzip 1ph.zip
cd 1ph
npm install
```

---

## Step 2 — Supabase Setup

1. Go to supabase.com → New project
2. Copy your project URL and anon key
3. Copy your database connection string (Settings → Database → Connection string → URI)

---

## Step 3 — Environment Variables

Copy `.env.example` to `.env.local` (web) and `.env` (pipeline):

```bash
cp .env.example apps/web/.env.local
cp .env.example apps/pipeline/.env
```

Fill in all values. See `.env.example` for descriptions.

---

## Step 4 — Database Migration

```bash
cd packages/db
npx prisma migrate dev --name init
npx prisma generate
```

---

## Step 5 — OAuth Setup

**Google:**
1. console.cloud.google.com → New project
2. APIs & Services → Credentials → OAuth 2.0 Client IDs
3. Authorized redirect URIs: `http://localhost:3000/api/auth/callback/google`
4. Copy Client ID + Secret to .env.local

**GitHub:**
1. github.com/settings/developers → New OAuth App
2. Callback URL: `http://localhost:3000/api/auth/callback/github`
3. Copy Client ID + Secret to .env.local

---

## Step 6 — Start Dev Environment

```bash
chmod +x scripts/dev.sh && ./scripts/dev.sh
```

This starts:
- `apps/web` on http://localhost:3000
- `apps/pipeline` on http://localhost:3001

---

## Step 7 — Seed Test Data (optional)

```bash
cd apps/pipeline
npm run seed
```

Inserts 10 sample hackathons for UI development.

---

## Step 8 — Open MASTER_PROMPT.md

Copy the prompt block into Claude Code / Cursor / Windsurf.
Start with TASK_001.md.

---

## Deployment

**Frontend (Vercel):**
```bash
cd apps/web
vercel --prod
```
Set all env vars in Vercel dashboard.

**Pipeline (Railway):**
- Connect GitHub repo to Railway (`h55n/1ph`)
- Set root directory: `apps/pipeline`
- Set build command: `npm run build`
- Set start command: `npm run start`
- Set healthcheck path: `/health`
- Use Node.js 20.x runtime
- Set Railway env vars:
  - `DATABASE_URL`
  - `REDIS_URL`
  - `PIPELINE_WEBHOOK_SECRET`
  - `PORT` (optional; Railway injects this automatically)
- Set GitHub repo secrets:
  - `PIPELINE_WEBHOOK_URL=https://pipeline-production-db4b.up.railway.app/trigger` (current production URL; use your Railway service URL in other environments)
  - `PIPELINE_WEBHOOK_SECRET` (must match Railway exactly)
- Railway auto-deploys on push to main

**Post-deploy validation:**
- Health: `GET https://pipeline-production-db4b.up.railway.app/health`
- Trigger:
  ```bash
  curl -X POST "https://pipeline-production-db4b.up.railway.app/trigger" \
    -H "Authorization: Bearer <PIPELINE_WEBHOOK_SECRET>" \
    -H "Content-Type: application/json"
  ```
- Confirm Railway logs show queued connector jobs and worker execution

**If Railway build fails, use the final error line:**
- `Cannot find module '@prisma/client'` → confirm root directory is `apps/pipeline` and build command is `npm run build` (this build script runs `prisma generate` before `tsc`)
- `Prisma schema not found` → confirm service is building from `apps/pipeline` (schema path is relative to that directory)
- `tsc` errors → fix TypeScript errors in the file reported by the final log lines
- Puppeteer/Chromium install errors → keep Railway default apt packages, then redeploy cleanly

**GitHub Actions:**
- Set `PIPELINE_WEBHOOK_URL` secret in GitHub repo settings
- The daily cron workflow in `.github/workflows/pipeline-trigger.yml` fires at 02:00 UTC
