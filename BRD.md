# 1ph — Business Requirements Document
**Version:** 1.1.0  
**Date:** 2026-04-14  
**Status:** Approved for Development  
**Color Palette:** #26150B (Dark Espresso) · #91B2DD (Steel Blue)  
**Font Pair:** DM Serif Display (headings) · JetBrains Mono (data/labels/tags) · Inter (body)

---

## 1. Executive Summary

**1ph** (One Place for Hackathons) is a clean, minimal, no-fluff global hackathon directory that aggregates every major hackathon — global and India-specific — into a single, fast, elegantly designed platform. Users browse, filter, and get redirected to apply. Organizers submit via a Google Form and are manually verified before going live. The platform wins on quality, freshness, and prestige clarity — not volume.

---

## 2. Problem Statement

The hackathon discovery experience is broken in three specific ways:

1. **Fragmentation.** Devpost covers global, Devfolio covers India, Unstop mixes hackathons with case studies and quizzes, MLH covers student events — no single source covers all with equal quality.
2. **Clutter.** Existing platforms are ad-heavy, noisy, and built for organizer revenue, not participant discovery. Finding the right hackathon requires visiting 4–5 platforms.
3. **No credibility signal.** A $500K prize Google hackathon sits next to an unverified club event with no visual distinction.

**1ph solves all three:** one directory, zero clutter, clear prestige layer.

---

## 3. Mission Statement

> *To be the cleanest, most complete, and most trustworthy directory of hackathons on the internet — built for builders, by builders.*

---

## 4. Target User Personas

### Persona A — The Competitive Builder
- **Who:** Developer, 20–28, has done 3+ hackathons
- **Goal:** Find high-prestige, high-prize hackathons fast. No noise.
- **Frustration:** "I have to check Devpost, MLH, and LinkedIn separately every week."
- **Key filters:** Prestige tier, prize pool, deadline, online/offline

### Persona B — The First-Timer
- **Who:** Student, 17–21, CS/engineering, wants their first hackathon
- **Goal:** Find something accessible, free, online, beginner-friendly
- **Frustration:** "I don't know which one to pick or if I even qualify."
- **Key filters:** Eligibility (students only), free entry, team size, theme, mode

---

## 5. Goals & Success Metrics

| Goal | Metric | 90-Day Target |
|------|--------|---------------|
| Complete hackathon directory | # of active hackathons indexed | 500+ listings |
| Data freshness | Pipeline staleness rate | <24hr lag |
| High utility, low bounce | Avg hackathon cards viewed/session | 3+ |
| Organizer adoption | Verified self-submitted hackathons | 30+ |
| Zero login friction for browsing | % sessions without login | 90%+ |

---

## 6. Feature Specification

### 6.1 MVP (v1)

| # | Feature | Description |
|---|---------|-------------|
| F01 | Hackathon Directory | Paginated, filterable, sortable card grid |
| F02 | Hackathon Detail Page | Full info + [Apply Now →] CTA redirects to source |
| F03 | Filter System | Theme, Mode, Fee, Team Size, Eligibility, Duration |
| F04 | Sort System | Prestige tier · deadline · prize pool · newest |
| F05 | Prestige Tier Badges | T1/T2 visual badge — rules-based, admin-reviewable |
| F06 | Scope Toggle | Global / India / All at directory top |
| F07 | Search | Full-text across name, organizer, tags |
| F08 | Data Pipeline | Daily automated aggregator — 11 sources |
| F09 | Organizer Submission | Google Form link; admin manually reviews and enters |
| F10 | Admin Panel | Approve/reject submissions, manage listings, view pipeline logs |
| F11 | Deadline Status Labels | Closing Soon (≤7d) · Open · Upcoming · Closed |
| F12 | Optional User Auth | Google/GitHub login — no browsing gate |
| F13 | Bookmark / Save | Logged-in users save hackathons |
| F14 | Closed Section | Closed hackathons under "Closed" filter tab — not default view |

### 6.2 Post-v1

- Deadline email/push reminders
- "Applied" tracker + personal dashboard
- Hackathon team finder
- Organizer self-serve portal with analytics (replaces Google Form)
- Sponsored/featured listings
- Mobile app
- Community reviews/ratings

### 6.3 Out of Scope (v1)

- No in-platform application forms — always redirect
- No team management
- No payment processing
- No unsponsored college-club hackathons
- No case studies, quizzes, debates
- No self-serve organizer portal — Google Form + manual review only

---

## 7. Data Model

### 7.1 Hackathon

```prisma
model Hackathon {
  id                String    @id @default(uuid())
  title             String
  slug              String    @unique
  organizerName     String
  organizerLogoUrl  String?
  description       String    // max 500 chars
  longDescription   String?
  themeTags         String[]
  mode              Mode
  entryFee          Decimal?
  entryFeeCurrency  String?
  teamSizeMin       Int
  teamSizeMax       Int?
  eligibility       Eligibility
  durationType      DurationType
  prizePool         Decimal?
  prizeCurrency     String?
  prizeDescription  String?
  registrationOpen  DateTime
  registrationClose DateTime
  eventStart        DateTime
  eventEnd          DateTime?
  applyUrl          String
  source            Source
  sourceId          String?
  scope             Scope
  indiaRegion       String?
  prestigeTier      PrestigeTier
  sponsors          String[]
  status            HackStatus
  isVerified        Boolean   @default(false)
  isFeatured        Boolean   @default(false)
  createdAt         DateTime  @default(now())
  updatedAt         DateTime  @updatedAt
  lastSyncedAt      DateTime?

  bookmarks         Bookmark[]
}

enum Mode         { ONLINE OFFLINE HYBRID }
enum Eligibility  { STUDENTS OPEN PROFESSIONALS }
enum DurationType { HR24 HR48 WEEK MONTH CUSTOM }
enum Source       { DEVPOST DEVFOLIO MLH UNSTOP DORAHACKS HACKEREARTH
                   STARTUP_INDIA HACK2SKILL HACKERRANK TOPLANG MANUAL }
enum Scope        { GLOBAL INDIA }
enum PrestigeTier { T1 T2 T3 }
enum HackStatus   { UPCOMING OPEN CLOSING_SOON CLOSED }
```

### 7.2 User

```prisma
model User {
  id         String     @id @default(uuid())
  email      String     @unique
  name       String
  avatarUrl  String?
  role       UserRole   @default(VISITOR)
  provider   Provider
  createdAt  DateTime   @default(now())
  bookmarks  Bookmark[]
}

enum UserRole { VISITOR ADMIN }
enum Provider { GOOGLE GITHUB }
```

### 7.3 Bookmark

```prisma
model Bookmark {
  id           String    @id @default(uuid())
  userId       String
  hackathonId  String
  createdAt    DateTime  @default(now())
  user         User      @relation(fields: [userId], references: [id])
  hackathon    Hackathon @relation(fields: [hackathonId], references: [id])
  @@unique([userId, hackathonId])
}
```

### 7.4 Organizer Submission

```prisma
model OrganizerSubmission {
  id              String           @id @default(uuid())
  submittedBy     String           // email from Google Form
  orgName         String
  orgWebsite      String
  hackathonTitle  String
  applyUrl        String
  rawFormData     Json             // full Google Form response
  status          SubmissionStatus @default(PENDING)
  adminNotes      String?
  reviewedAt      DateTime?
  createdAt       DateTime         @default(now())
}

enum SubmissionStatus { PENDING APPROVED REJECTED }
```

### 7.5 Pipeline Run Log

```prisma
model PipelineRun {
  id            String       @id @default(uuid())
  source        Source
  runAt         DateTime     @default(now())
  status        PipelineStatus
  newCount      Int
  updatedCount  Int
  closedCount   Int
  errorLog      String?
}

enum PipelineStatus { SUCCESS PARTIAL FAILED }
```

---

## 8. Prestige Tier System

### Tier Rules Engine

```
TIER 1 — Elite
  Conditions (ANY):
    organizer IN t1_orgs_list
    prize_pool >= $50,000 USD / ₹40L
    source == MLH AND edition_count >= 3

  t1_orgs_list (hardcoded in tier-engine/t1-orgs.ts):
    Global: Google, Meta, Microsoft, Amazon, GitHub, NASA, OpenAI,
            Anthropic, Goldman Sachs, JPMorgan, UN Agencies, Ethereum Foundation
    India:  Flipkart, Walmart Global Tech, NASSCOM, DPIIT/Startup India nationals,
            IIT-organized national hackathons, ISRO, NIC (Govt of India),
            Smart India Hackathon (SIH)

TIER 2 — Established
  Conditions (ANY):
    prize_pool >= $5,000 / ₹4L
    is_verified AND sponsors[] non-empty
    college hackathon (IIT/NIT/BITS) WITH named corporate sponsor
    source IN [DEVPOST, DEVFOLIO, DORAHACKS] AND verifiable history

TIER 3 — Community
  Condition: passes quality gate, doesn't meet T1 or T2
  No badge displayed — clean card
```

### Quality Gate (mandatory before DB entry)

- Has `registrationClose` date
- `applyUrl` resolves HTTP 200
- Has `title` and `organizerName`
- Title/description does NOT match keyword blocklist: `["quiz", "case study", "debate", "trivia", "essay", "management competition"]`
- Not a duplicate (`sourceId` dedup + fuzzy title match ≤ Levenshtein 10)
- **College hackathons:** Only accepted if `sponsors[]` is non-empty with a verifiable named sponsor

---

## 9. Data Pipeline — Complete Source List

| # | Source | Method | Scope | Notes |
|---|--------|--------|-------|-------|
| 1 | Devpost | Puppeteer scraper | Global | /hackathons?sort_by=Upcoming |
| 2 | Devfolio | GraphQL API | India | Stable undoc endpoint |
| 3 | MLH | Axios + Cheerio | Global | mlh.io/seasons |
| 4 | Unstop | Puppeteer scraper | India | Filter: hackathons/build-a-thons only |
| 5 | DoraHacks | REST API | Global | dorahacks.io/api — public |
| 6 | HackerEarth | REST API | Both | Developer API |
| 7 | Startup India | Axios + Cheerio | India | startupindia.gov.in — SIH + DPIIT |
| 8 | Hack2Skill | Axios + Cheerio | India | Major India aggregator |
| 9 | HackerRank | Puppeteer scraper | Global | Filter to hack/build tag only |
| 10 | Toplang | Axios + Cheerio | India | Secondary India source |
| 11 | Organizer submissions | Manual (Google Form) | Both | Admin reviews before going live |

### Pipeline Flow

```
CRON (02:00 UTC daily)
  → SOURCE CONNECTORS (one BullMQ worker per source)
  → NORMALIZATION LAYER (source schema → Hackathon model)
  → QUALITY GATE (fields · URL check · keyword filter · dedup · sponsor check)
  → PRESTIGE TIER ENGINE (T1/T2/T3 assignment)
  → UPSERT TO DB (INSERT new · UPDATE changed · CLOSED sweep)
  → LOG pipeline_run{}
```

### Deduplication

- Primary: `source` + `sourceId` composite unique
- Secondary: fuzzy title + same `registrationClose` date → admin flag
- URL match: identical `applyUrl` across sources → keep highest-tier source record

### Status Sweep (runs daily after pipeline)

```
today > registrationClose                     → CLOSED
today >= registrationClose - 7d               → CLOSING_SOON
today < registrationOpen                      → UPCOMING
else                                          → OPEN
applyUrl non-200 for 3 consecutive runs       → flag for admin review
applyUrl non-200 for 7 days                   → auto-CLOSED
```

### Closed Hackathons Policy

Closed hackathons remain in DB and are visible under the "Closed" filter tab. Hidden from default Open view. This preserves historical data, supports prestige scoring (edition_count), and provides organizer credibility signals.

---

## 10. Organizer Submission Flow (v1)

```
1. User clicks "Submit a Hackathon" → redirected to Google Form (no login)
2. Google Form collects: org name, email, website, hackathon title,
   description, apply URL, dates, mode, prize, fee, team size,
   eligibility, theme tags, sponsors
3. Form → Google Sheets → admin notification
4. Admin reviews → manually enters approved hackathons into DB
5. Goes live with isVerified = true
```

v1 rationale: Google Form = zero build cost, full quality control. Replace with self-serve portal in v2.

---

## 11. UI/UX Specification

### Design Tokens

| Token | Value |
|-------|-------|
| Background | `#26150B` |
| Accent | `#91B2DD` |
| Card surface | `#321C0E` |
| Border | `#4A2E18` |
| Text primary | `#F5EDE3` |
| Text muted | `#9E8A7A` |
| Tag bg | `#3D2415` |
| Open | `#6DBF8E` |
| Closing Soon | `#E8C468` |
| Upcoming | `#91B2DD` |
| Closed | `#4A3A30` |
| Heading | DM Serif Display |
| Mono/tags | JetBrains Mono |
| Body | Inter |
| Border radius | 8px cards · 4px chips |

### Pages

```
/                    → Directory (default: Open + All)
/hackathon/[slug]    → Detail page
/bookmarks           → Auth-gated
/submit              → Links to Google Form
/admin               → Admin panel (admin role only)
/login               → Google / GitHub OAuth
```

### Animations

- Card hover: 2px lift + left border accent (150ms ease-out)
- Filter dropdown: slide-down (180ms)
- Page load: staggered card fade-in (40ms per card, max 8)
- CLOSING SOON chip: subtle pulse only
- Tab switch: 120ms crossfade
- Skeleton loaders on fetch

---

## 12. SEO Requirements

- Unique `<title>` + `<meta description>` per hackathon page
- Auto-generated OG image per hackathon (title + org + deadline on dark bg, via @vercel/og)
- JSON-LD Event schema on all detail pages
- Auto-generated `/sitemap.xml` from DB
- SSG for directory (Next.js static generation)
- Canonical URLs everywhere
- All copy written with writing-god skill — no filler, no AI fingerprint

---

## 13. Technical Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 App Router |
| Styling | Tailwind CSS |
| Database | PostgreSQL via Supabase |
| ORM | Prisma |
| Auth | NextAuth.js (Google + GitHub) |
| Pipeline | Node.js + BullMQ |
| Scraping (JS pages) | Puppeteer |
| Scraping (static) | Axios + Cheerio |
| Cron | GitHub Actions (free, reliable) |
| Pipeline hosting | Railway |
| Frontend hosting | Vercel |
| OG image gen | @vercel/og |
| Storage | Supabase Storage |
| Search v1 | Postgres full-text |
| Search v2 | Meilisearch |

---

## 14. Risk Register

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|------------|
| R1 | Devpost/Unstop block scrapers | High | High | Rotate user-agents, request delays, proxy for heavy sources |
| R2 | Stale data → trust erosion | Medium | High | `lastSyncedAt` in admin; "Report issue" on every card; URL health alerts |
| R3 | Google Form spam | Medium | Medium | Manual review catches all before going live; honeypot field |
| R4 | Prestige tier misassignment | Low | High | T1 list version-controlled; admin can override any tier |
| R5 | Apply URLs go dead | High | Low | Daily URL check; auto-CLOSED after 7 days of failures |
| R6 | India regional gaps | Medium | Medium | Hack2Skill + Devfolio + Unstop covers 80%; Google Form captures rest |

---

## 15. Critical Assumptions

1. Daily scraping of major sources is feasible without persistent blocks
2. Google Form + manual review is sustainable under ~20 submissions/week
3. Quality gate filters >80% noise without manual review at scale
4. Users are fine being redirected to apply (no in-platform forms)
5. Hardcoded T1 list is maintainable for v1 (<60 orgs)
6. Supabase free tier handles v1 data volume (~5,000 records max)

---

## 16. Resolved Decisions

| Decision | Resolution |
|----------|------------|
| India scope | Major cities first. Pan-India v2. |
| Small hackathon quality threshold | Exclude unsponsored college-club. Include if named corporate sponsor. |
| Organizer verification | Google Form + manual admin review for v1. Self-serve portal v2. |
| Closed hackathons | Keep in DB. Visible under "Closed" tab. Hidden from default view. |
| SEO copy | Written using writing-god skill. No filler anywhere. |

---

*v1.1.0 — All open questions resolved. Ready for development.*
