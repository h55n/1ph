# API_CONTRACTS.md — 1ph

Internal API routes used by the Next.js frontend.
All routes are in `apps/web/app/api/`.

---

## Auth

Handled entirely by NextAuth.js.
Route: `/api/auth/[...nextauth]`
No custom logic needed beyond configuration.

---

## Bookmarks

### POST /api/bookmarks
Add a bookmark.

**Auth:** Required (session)  
**Body:**
```json
{ "hackathonId": "uuid" }
```
**Response 201:**
```json
{ "id": "uuid", "hackathonId": "uuid", "userId": "uuid" }
```
**Response 401:** Not authenticated  
**Response 409:** Already bookmarked

---

### DELETE /api/bookmarks/[hackathonId]
Remove a bookmark.

**Auth:** Required (session)  
**Response 200:** `{ "deleted": true }`  
**Response 401:** Not authenticated  
**Response 404:** Bookmark not found

---

### GET /api/bookmarks
Get all bookmarks for current user.

**Auth:** Required (session)  
**Response 200:**
```json
{
  "bookmarks": [
    { "hackathonId": "uuid", "createdAt": "ISO" }
  ]
}
```

---

## OG Image

### GET /api/og?slug=[slug]
Generate Open Graph image for a hackathon.

**Auth:** None  
**Returns:** PNG image (1200×630)  
**Generated with:** @vercel/og  
**Design:** Dark bg (#26150B), title in DM Serif Display, org + deadline in JetBrains Mono

---

## Pipeline Trigger (apps/pipeline)

### POST /trigger
Trigger a full pipeline run. Called by GitHub Actions.

**Auth:** Bearer token (PIPELINE_WEBHOOK_SECRET)  
**Response 200:** `{ "queued": true, "sources": 10 }`  
**Response 401:** Invalid or missing token  

---

## Admin Routes

All admin routes check `session.user.role === 'ADMIN'` — return 403 if not.

### GET /api/admin/submissions
List organizer submissions.

**Query params:** `status=PENDING|APPROVED|REJECTED|all` (default: PENDING)  
**Response 200:**
```json
{
  "submissions": [
    {
      "id": "uuid",
      "orgName": "string",
      "hackathonTitle": "string",
      "submittedBy": "email",
      "status": "PENDING",
      "createdAt": "ISO"
    }
  ]
}
```

### POST /api/admin/submissions/[id]/approve
Mark submission approved + create Hackathon record.

**Body:** Full hackathon fields (admin fills in form pre-populated from submission)  
**Response 200:** `{ "hackathonId": "uuid" }`

### POST /api/admin/submissions/[id]/reject
**Body:** `{ "adminNotes": "string" }`  
**Response 200:** `{ "rejected": true }`

### PATCH /api/admin/hackathons/[id]
Update tier, featured status, or any field.

**Body:** Partial Hackathon fields  
**Response 200:** Updated hackathon object

### GET /api/admin/pipeline-runs
Get recent pipeline run logs.

**Query:** `?limit=50` (default 50)  
**Response 200:** Array of PipelineRun records
