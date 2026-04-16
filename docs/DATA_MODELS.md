# DATA_MODELS.md — 1ph

Complete data model reference. See packages/db/schema.prisma for the authoritative Prisma schema.

---

## Hackathon

The core entity. Every record comes from the pipeline or manual admin entry.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | uuid | ✓ | Auto-generated |
| title | string | ✓ | |
| slug | string | ✓ | Unique, URL-safe, auto-generated from title |
| organizerName | string | ✓ | |
| organizerLogoUrl | string | — | Optional |
| description | string | ✓ | Max 500 chars, shown on card + detail |
| longDescription | string | — | Shown on detail page only |
| themeTags | string[] | ✓ | AI/ML, Web3, Fintech, Health, Open, etc. |
| mode | enum | ✓ | ONLINE \| OFFLINE \| HYBRID |
| entryFee | decimal | — | null = free |
| entryFeeCurrency | string | — | Default USD |
| teamSizeMin | int | ✓ | Default 1 |
| teamSizeMax | int | — | null = no max |
| eligibility | enum | ✓ | STUDENTS \| OPEN \| PROFESSIONALS |
| durationType | enum | ✓ | HR24 \| HR48 \| WEEK \| MONTH \| CUSTOM |
| prizePool | decimal | — | null = no prize or unspecified |
| prizeCurrency | string | — | Default USD |
| prizeDescription | string | — | Human-readable: "₹5L + internship" |
| registrationOpen | DateTime | — | |
| registrationClose | DateTime | ✓ | Required by quality gate |
| eventStart | DateTime | ✓ | |
| eventEnd | DateTime | — | |
| applyUrl | string | ✓ | External only — validated by quality gate |
| source | enum | ✓ | DEVPOST \| DEVFOLIO \| MLH \| ... \| MANUAL |
| sourceId | string | — | Original ID on source platform (for dedup) |
| scope | enum | ✓ | GLOBAL \| INDIA |
| indiaRegion | string | — | "Mumbai" \| "Bangalore" \| "Pan-India" |
| prestigeTier | enum | ✓ | T1 \| T2 \| T3 — assigned by tier engine |
| sponsors | string[] | — | Used in quality gate + tier rules |
| status | enum | ✓ | UPCOMING \| OPEN \| CLOSING_SOON \| CLOSED |
| isVerified | boolean | ✓ | true = admin-approved or verified submission |
| isFeatured | boolean | ✓ | future sponsored flag — default false |
| urlHealthFails | int | ✓ | Consecutive pipeline URL check failures |
| createdAt | DateTime | ✓ | Auto |
| updatedAt | DateTime | ✓ | Auto |
| lastSyncedAt | DateTime | — | Set by pipeline on each successful fetch |

**Indexes:** status, scope, prestigeTier, registrationClose  
**Unique:** [source, sourceId]

---

## User

| Field | Type | Notes |
|-------|------|-------|
| id | uuid | |
| email | string | Unique |
| name | string | |
| avatarUrl | string | Optional |
| role | enum | VISITOR (default) \| ADMIN |
| provider | enum | GOOGLE \| GITHUB |
| createdAt | DateTime | |

---

## Bookmark

Join table between User and Hackathon.

| Field | Type | Notes |
|-------|------|-------|
| id | uuid | |
| userId | FK → User | Cascade delete |
| hackathonId | FK → Hackathon | Cascade delete |
| createdAt | DateTime | |

**Unique:** [userId, hackathonId] — no double bookmarks

---

## OrganizerSubmission

Captures Google Form responses for admin review.

| Field | Type | Notes |
|-------|------|-------|
| id | uuid | |
| submittedBy | string | Email from form |
| orgName | string | |
| orgWebsite | string | |
| hackathonTitle | string | |
| applyUrl | string | |
| rawFormData | JSON | Full form response |
| status | enum | PENDING (default) \| APPROVED \| REJECTED |
| adminNotes | string | Optional review notes |
| reviewedAt | DateTime | Set when admin acts |
| createdAt | DateTime | |

---

## PipelineRun

One record per source per pipeline execution.

| Field | Type | Notes |
|-------|------|-------|
| id | uuid | |
| source | enum | Which connector ran |
| runAt | DateTime | |
| status | enum | SUCCESS \| PARTIAL \| FAILED |
| newCount | int | New hackathons inserted |
| updatedCount | int | Existing hackathons updated |
| closedCount | int | Hackathons auto-closed this run |
| errorLog | string | Error details if PARTIAL/FAILED |

**Indexes:** runAt, source

---

## Status Calculation Logic

```
today > registrationClose           → CLOSED
today >= registrationClose - 7 days → CLOSING_SOON
today < registrationOpen            → UPCOMING
else                                → OPEN
```

Runs daily after pipeline completes. Also:
- urlHealthFails increments on each failed URL check
- Auto-CLOSED when urlHealthFails >= 7
