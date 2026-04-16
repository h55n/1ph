# TASK_001 — Foundation: Monorepo + DB + Auth + Base Layout

**Phase:** 1  
**Estimated time:** 3–4 hours  
**Done when:** Dev server runs, DB is connected, login with Google/GitHub works, base layout renders

---

## Subtasks

### 1.1 — Init Turborepo
```bash
npx create-turbo@latest 1ph --package-manager npm
```
- Rename packages to: apps/web, apps/pipeline, packages/db
- Configure turbo.json with build + dev + lint pipelines

### 1.2 — Prisma Setup
- Copy schema.prisma from packages/db/schema.prisma (already in ZIP)
- Install: `npm install prisma @prisma/client --workspace=packages/db`
- Run: `npx prisma migrate dev --name init`
- Run: `npx prisma generate`

### 1.3 — NextAuth.js Setup (apps/web)
- Install: `npm install next-auth`
- Create `apps/web/app/api/auth/[...nextauth]/route.ts`
- Configure Google + GitHub providers
- Add User, Account, Session, VerificationToken models (already in schema)
- Protect /admin route: check role === ADMIN, redirect otherwise

### 1.4 — Tailwind + Design Tokens (apps/web)
Install and configure Tailwind. Add these custom tokens to tailwind.config.ts:
```js
colors: {
  bg: '#26150B',
  accent: '#91B2DD',
  card: '#321C0E',
  border: '#4A2E18',
  'text-primary': '#F5EDE3',
  'text-muted': '#9E8A7A',
  'tag-bg': '#3D2415',
  open: '#6DBF8E',
  closing: '#E8C468',
  upcoming: '#91B2DD',
  closed: '#4A3A30',
}
```
Add Google Fonts: DM Serif Display + JetBrains Mono + Inter via next/font.

### 1.5 — Base Layout
Build `apps/web/app/layout.tsx`:
- Header: "1ph" logo (DM Serif Display), [Login] button, [Submit +] button
- Footer: minimal — "© 1ph" + link to submit form
- Background: #26150B full page
- No sidebar

### 1.6 — Verify
- `npm run dev` starts without errors
- http://localhost:3000 renders with header + dark background
- /login → Google OAuth → user created in DB
- /admin → redirects non-admin users

---

## Definition of Done
- [ ] Turborepo monorepo running
- [ ] Prisma schema migrated to Supabase
- [ ] Google + GitHub login working
- [ ] Base layout renders (header + footer + dark bg)
- [ ] /admin redirects non-admins
- [ ] No TypeScript errors
