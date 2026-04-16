# TASK_004 — Admin Panel

**Phase:** 4  
**Estimated time:** 2–3 hours  
**Done when:** Admin can review submissions, manage hackathons, view pipeline logs

---

## Subtasks

### 4.1 — Admin Layout + Auth Gate
`apps/web/app/admin/layout.tsx`
- Check session.user.role === 'ADMIN'
- If not admin: redirect to /
- Simple sidebar nav: Submissions | Hackathons | Pipeline | Duplicates

### 4.2 — Submissions Queue
`apps/web/app/admin/submissions/page.tsx`
- Table: org name, hackathon title, submitted by, date, status (PENDING/APPROVED/REJECTED)
- Filter: PENDING only (default) | All
- Actions per row:
  - [Approve] → opens edit form pre-filled with submission data → admin completes + saves → creates Hackathon record (isVerified: true)
  - [Reject] → marks submission as REJECTED, admin can add notes
- Show raw form data expandable section

### 4.3 — Hackathon Manager
`apps/web/app/admin/hackathons/page.tsx`
- Table of all hackathons: title, source, tier, status, lastSyncedAt, urlHealthFails
- Inline editable: prestigeTier (override dropdown), isFeatured (toggle)
- Actions: Edit (full edit form), Delete
- Filters: by source, by status, by tier
- Show urlHealthFails > 0 as warning indicator

### 4.4 — Pipeline Logs
`apps/web/app/admin/pipeline/page.tsx`
- Table of recent PipelineRun records (last 30 days)
- Columns: source, runAt, status, newCount, updatedCount, closedCount
- Color code: SUCCESS (green) / PARTIAL (amber) / FAILED (red)
- Expandable errorLog per row
- Summary: last run time per source

### 4.5 — Duplicate Flagging
`apps/web/app/admin/duplicates/page.tsx`
- Show hackathons flagged as probable duplicates by dedup engine
- Display side-by-side for easy comparison
- Actions: [Keep both] [Mark as duplicate → delete one]

---

## Definition of Done
- [ ] /admin redirects non-admins
- [ ] Submissions queue shows PENDING submissions
- [ ] Admin can approve → hackathon goes live
- [ ] Admin can reject with notes
- [ ] Hackathon manager shows all listings with tier override
- [ ] Pipeline logs table renders with correct status colors
- [ ] No public user can access any /admin route
