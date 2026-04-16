# TASK_007 — Deploy

**Phase:** 7  
**Estimated time:** 1–2 hours  
**Done when:** Both services live, pipeline runs successfully, hackathons visible on production

---

## Pre-Deploy Checklist
- [ ] All env vars documented in .env.example
- [ ] No hardcoded URLs (all use env vars)
- [ ] `npm run build` succeeds locally without errors
- [ ] `npx prisma migrate deploy` runs without errors
- [ ] Admin email set in ADMIN_EMAIL env var

---

## 7.1 — Supabase Production Setup
1. Create production project at supabase.com
2. Run: `DATABASE_URL=[prod-url] npx prisma migrate deploy`
3. Verify tables created in Supabase Table Editor

## 7.2 — Deploy Pipeline to Railway
1. Push repo to GitHub
2. Railway → New Project → Deploy from GitHub repo
3. Set root directory: `apps/pipeline`
4. Set all env vars (DATABASE_URL, REDIS_URL, PIPELINE_WEBHOOK_SECRET)
5. Railway provides a public URL — copy it
6. Test: POST to `[railway-url]/trigger` → should queue jobs

## 7.3 — Deploy Frontend to Vercel
1. Vercel → New Project → Import GitHub repo
2. Set root directory: `apps/web`
3. Build command: `npm run build`
4. Set all env vars (DATABASE_URL, NEXTAUTH_*, GOOGLE_*, GITHUB_*, SUPABASE_*)
5. Set NEXTAUTH_URL to your Vercel domain

## 7.4 — Update OAuth Redirect URIs
**Google Cloud Console:**
- Add: `https://your-domain.vercel.app/api/auth/callback/google`

**GitHub Developer Settings:**
- Update callback URL to: `https://your-domain.vercel.app/api/auth/callback/github`

## 7.5 — GitHub Actions Setup
In GitHub repo Settings → Secrets:
- `PIPELINE_WEBHOOK_URL` = Railway service URL + /trigger
- `PIPELINE_WEBHOOK_SECRET` = same value as in Railway env

Test: Actions → pipeline-trigger → Run workflow manually

## 7.6 — First Pipeline Run
1. Trigger pipeline manually from GitHub Actions
2. Monitor Railway logs — each connector should log start/end
3. Check Supabase — hackathons table should populate
4. Check production site — directory should show hackathons

## 7.7 — Smoke Test
- [ ] Browse directory — hackathons visible
- [ ] Filter by theme — results update
- [ ] Click a hackathon — detail page loads
- [ ] Click Apply Now — redirects to external URL in new tab
- [ ] Login with Google — works
- [ ] Bookmark a hackathon — saved
- [ ] /submit — Google Form link works
- [ ] /admin (as admin user) — accessible
- [ ] /admin (as regular user) — redirects to /

---

## Post-Deploy
- Set yourself as ADMIN in Supabase:
  ```sql
  UPDATE "User" SET role = 'ADMIN' WHERE email = 'your@email.com';
  ```
- Monitor first 3 pipeline runs for errors
- Check /admin/pipeline for run logs
