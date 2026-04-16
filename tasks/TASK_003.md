# TASK_003 — Detail Pages + Auth + Bookmarks + Submit

**Phase:** 3  
**Estimated time:** 3–4 hours  
**Done when:** Detail pages work, bookmarks work, /submit links to form, /login works

---

## Subtasks

### 3.1 — Hackathon Detail Page
`apps/web/app/hackathon/[slug]/page.tsx`

Sections in order:
1. **Header:** Title (DM Serif Display, large), organizer logo + name, prestige badge, scope indicator
2. **Status bar:** StatusChip + "X days left" countdown to registration close
3. **Quick stats row:** Prize · Entry fee · Team size · Mode · Duration (JetBrains Mono)
4. **[Apply Now →] CTA button** — large, accent color, opens applyUrl in new tab
   - NEVER in-platform. Always `target="_blank" rel="noopener noreferrer"`
   - If status = CLOSED: button disabled, text "Registration Closed"
5. **Description:** longDescription ?? description
6. **Eligibility:** eligibility enum displayed as plain text
7. **Theme tags:** all themeTags as chips
8. **Sponsors:** sponsors[] displayed as text list (if non-empty)
9. **Source attribution:** small muted text: "Listed from Devpost" or "Verified submission"
10. **Bookmark button:** top-right of page, auth-gated (prompts login if not logged in)

SSG with generateStaticParams (all hackathon slugs).
Fallback: `blocking` (new hackathons added after build get SSR on first visit).

### 3.2 — OG Image Generation
`apps/web/app/api/og/route.tsx`
Using @vercel/og. Design:
- #26150B background
- Hackathon title (DM Serif Display, large, #F5EDE3)
- Organizer name (JetBrains Mono, small, #9E8A7A)
- Deadline (JetBrains Mono, small, #E8C468)
- 1ph logo bottom-right
- Size: 1200×630

### 3.3 — SEO Metadata per Detail Page
In each /hackathon/[slug]/page.tsx:
```tsx
export async function generateMetadata({ params }) {
  // fetch hackathon by slug
  return {
    title: `${hackathon.title} | 1ph`,
    description: hackathon.description,
    openGraph: {
      title: hackathon.title,
      description: hackathon.description,
      images: [`/api/og?slug=${params.slug}`],
    }
  }
}
```
Also add JSON-LD Event schema as a `<script type="application/ld+json">` block.

### 3.4 — BookmarkButton Component
`apps/web/components/BookmarkButton.tsx`
- If not logged in: shows bookmark icon, click → redirect to /login
- If logged in: toggle bookmark state via API route
- Optimistic update (toggle immediately, revert on error)
- API route: POST/DELETE /api/bookmarks

### 3.5 — Bookmarks Page
`apps/web/app/bookmarks/page.tsx`
- Auth-gated: redirect to /login if not authenticated
- Fetches all bookmarks for current user
- Renders same HackathonGrid with user's saved hackathons
- Empty state: "No saved hackathons yet. Browse to find some."

### 3.6 — Submit Page
`apps/web/app/submit/page.tsx`
- Simple page — no form to build
- Headline: "List your hackathon on 1ph"
- Short description of what happens (submit → review → go live)
- Large [Submit via Google Form →] button linking to NEXT_PUBLIC_ORGANIZER_FORM_URL
- Opens in new tab
- Note below button: "We review all submissions within 48 hours."

### 3.7 — Login Page
`apps/web/app/login/page.tsx`
- Clean centered card on dark background
- "Continue with Google" button
- "Continue with GitHub" button
- No email/password — OAuth only

---

## Definition of Done
- [ ] Detail page renders all sections correctly
- [ ] Apply Now opens external URL in new tab
- [ ] Apply Now disabled + text changed when CLOSED
- [ ] OG image generates with correct data
- [ ] JSON-LD schema present on detail pages
- [ ] Bookmark toggles work (auth-gated)
- [ ] /bookmarks shows saved hackathons, redirects if not logged in
- [ ] /submit shows Google Form link (no in-platform form)
- [ ] /login shows Google + GitHub OAuth buttons
