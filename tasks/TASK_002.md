# TASK_002 — Directory: Cards + Grid + Filters + Search

**Phase:** 2  
**Estimated time:** 4–6 hours  
**Done when:** Directory page renders hackathon cards with working filters and search

---

## Subtasks

### 2.1 — HackathonCard Component
`apps/web/components/HackathonCard.tsx`

Fields to display (all from Hackathon model):
- Organizer logo (fallback: initials in accent color)
- Organizer name (JetBrains Mono, small, muted)
- Title (DM Serif Display, large)
- PrestigeBadge (T1 gold / T2 silver — T3 renders nothing)
- StatusChip (OPEN green / CLOSING_SOON amber pulse / UPCOMING accent / CLOSED muted)
- Prize: "$100K" or "₹5L" or "No prize listed" (muted)
- Entry fee: "FREE" or amount
- Deadline: "4 days left" (hover tooltip: exact date)
- Mode pill: Online / Offline / Hybrid
- Top 2 theme tags (JetBrains Mono, tag-bg background)
- Scope indicator: 🌐 or 🇮🇳

Card interactions:
- Hover: 2px translateY + left border accent highlight (150ms ease-out)
- Click: navigate to /hackathon/[slug]
- Closed hackathons: reduced opacity (0.6), no hover effect

### 2.2 — PrestigeBadge Component
`apps/web/components/PrestigeBadge.tsx`
- T1: gold chip, "T1" label in JetBrains Mono
- T2: silver chip, "T2" label
- T3: returns null (renders nothing)

### 2.3 — StatusChip Component
`apps/web/components/StatusChip.tsx`
- OPEN: #6DBF8E dot + "OPEN" text
- CLOSING_SOON: #E8C468 dot + "CLOSING SOON" — dot pulses
- UPCOMING: #91B2DD dot + "UPCOMING"
- CLOSED: muted dot + "CLOSED"

### 2.4 — HackathonGrid Component
`apps/web/components/HackathonGrid.tsx`
- Responsive: 1 col mobile, 2 col tablet (md:), 3 col desktop (lg:)
- Staggered fade-in on mount: 40ms delay per card, max 8 cards animated
- SkeletonCard for loading state (same dimensions as HackathonCard)

### 2.5 — FilterBar Component
`apps/web/components/FilterBar.tsx`
Dropdowns for:
- Theme: AI/ML, Web3, Fintech, Health, Open, Hardware, Social Impact
- Mode: Online, Offline, Hybrid
- Fee: Free, Paid
- Team size: Solo (1), 2–4, 5+
- Eligibility: Students, Open to all, Professionals
- Duration: 24hr, 48hr, Week-long, Month-long

Filter state in URL params (enables shareable filtered links).
Slide-down animation on dropdown open (180ms).

### 2.6 — ScopeToggle Component
`apps/web/components/ScopeToggle.tsx`
- Three tabs: "All" | "Global 🌐" | "India 🇮🇳"
- Active tab: accent underline
- Updates URL param ?scope=

### 2.7 — Sort Control
Sort options (dropdown):
- Prestige (default)
- Deadline (closest first)
- Prize pool (highest first)
- Newest added

### 2.8 — SearchBar Component
`apps/web/components/SearchBar.tsx`
- Debounced (300ms) Postgres full-text search
- Searches: title, organizerName, themeTags
- Updates URL param ?q=
- Clear button when query is active

### 2.9 — Directory Page
`apps/web/app/page.tsx`
- SSG with ISR: `revalidate: 3600` (refresh hourly)
- Read filters from URL searchParams
- Prisma query with where clause from active filters
- Show total count: "512 hackathons" above grid
- Default view: status = OPEN, scope = ALL, sort = prestige

---

## Definition of Done
- [ ] Cards render all fields correctly
- [ ] T1/T2 badges visible, T3 shows nothing
- [ ] Status chips show correct colors + CLOSING_SOON pulses
- [ ] Grid is responsive (1/2/3 col)
- [ ] Staggered fade-in works on page load
- [ ] All 6 filters work + update URL params
- [ ] Scope toggle works
- [ ] Sort works
- [ ] Search returns results with 300ms debounce
- [ ] Skeleton loaders show during fetch
- [ ] Closed hackathons at reduced opacity
