# CLAUDE.md — 1ph Project Rules

Re-read this file at the start of every session.

## Project
1ph — One Place for Hackathons. Clean, minimal hackathon directory.
Two runtimes: apps/web (Next.js, Vercel) + apps/pipeline (Node.js run via GitHub Actions).

## Stack (frozen)
Next.js 14 App Router · Tailwind CSS · Supabase/PostgreSQL · Prisma · NextAuth.js
BullMQ · Puppeteer · Axios+Cheerio · Turborepo · @vercel/og

## Colors (frozen — never change)
bg: #26150B  |  accent: #91B2DD  |  card: #321C0E  |  border: #4A2E18
text: #F5EDE3  |  muted: #9E8A7A  |  tag-bg: #3D2415
open: #6DBF8E  |  closing: #E8C468  |  upcoming: #91B2DD  |  closed: #4A3A30

## Fonts (frozen)
Headings: DM Serif Display  |  Mono/tags: JetBrains Mono  |  Body: Inter

## Hard Rules
- Pipeline workers NEVER go inside apps/web
- Apply Now ALWAYS opens applyUrl in new tab — never in-platform
- Quality gate runs on EVERY record before DB insert
- T1 org list lives ONLY in tier-engine/t1-orgs.ts
- Organizer submissions always start as PENDING — never auto-approve
- Closed hackathons stay in DB — only hidden from default Open view
- No inline styles — Tailwind only
- No localStorage / sessionStorage
- No hardcoded secrets — .env only

## File Ownership
- packages/db/schema.prisma — single source of truth for data model
- apps/pipeline/connectors/base.ts — IConnector interface, all connectors implement this
- apps/pipeline/tier-engine/t1-orgs.ts — T1 org list, nowhere else
- apps/web/app/page.tsx — directory home, SSG with revalidate: 3600

## When Uncertain
Ask before guessing. Document the decision in DECISIONS.md.
