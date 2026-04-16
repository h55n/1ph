# TASK_006 — SEO + Polish + Animations

**Phase:** 6  
**Estimated time:** 2–3 hours  
**Done when:** All SEO requirements met, animations match spec, fully responsive, WCAG AA

---

## Subtasks

### 6.1 — Sitemap
`apps/web/app/sitemap.ts`
```typescript
export default async function sitemap() {
  const hackathons = await prisma.hackathon.findMany({
    select: { slug: true, updatedAt: true },
    where: { status: { not: 'CLOSED' } }
  });
  return [
    { url: 'https://1ph.dev', lastModified: new Date() },
    ...hackathons.map(h => ({
      url: `https://1ph.dev/hackathon/${h.slug}`,
      lastModified: h.updatedAt,
    }))
  ];
}
```

### 6.2 — Robots.txt
`apps/web/app/robots.ts`
```typescript
export default function robots() {
  return {
    rules: { userAgent: '*', allow: '/', disallow: '/admin' },
    sitemap: 'https://1ph.dev/sitemap.xml',
  };
}
```

### 6.3 — Root Metadata
`apps/web/app/layout.tsx` — add metadata export:
```typescript
export const metadata = {
  title: '1ph — Every hackathon. One place.',
  description: 'The cleanest hackathon directory on the internet. Global + India hackathons, filtered by prestige, prize, and deadline. No clutter.',
  openGraph: {
    title: '1ph — Every hackathon. One place.',
    description: 'Global + India hackathons in one clean directory.',
    url: 'https://1ph.dev',
    siteName: '1ph',
    images: [{ url: '/og-default.png', width: 1200, height: 630 }],
  },
  twitter: { card: 'summary_large_image' },
  metadataBase: new URL('https://1ph.dev'),
};
```

### 6.4 — JSON-LD Event Schema (Detail Pages)
Add to /hackathon/[slug]/page.tsx:
```tsx
<script
  type="application/ld+json"
  dangerouslySetInnerHTML={{
    __html: JSON.stringify({
      "@context": "https://schema.org",
      "@type": "Event",
      "name": hackathon.title,
      "startDate": hackathon.eventStart,
      "endDate": hackathon.eventEnd,
      "eventStatus": hackathon.status === 'CLOSED'
        ? "https://schema.org/EventCancelled"
        : "https://schema.org/EventScheduled",
      "eventAttendanceMode": hackathon.mode === 'ONLINE'
        ? "https://schema.org/OnlineEventAttendanceMode"
        : "https://schema.org/OfflineEventAttendanceMode",
      "location": hackathon.mode === 'ONLINE'
        ? { "@type": "VirtualLocation", "url": hackathon.applyUrl }
        : { "@type": "Place", "name": hackathon.indiaRegion ?? "TBD" },
      "organizer": {
        "@type": "Organization",
        "name": hackathon.organizerName,
      },
      "offers": {
        "@type": "Offer",
        "price": hackathon.entryFee ?? 0,
        "priceCurrency": hackathon.entryFeeCurrency ?? "USD",
        "url": hackathon.applyUrl,
      }
    })
  }}
/>
```

### 6.5 — Animation Audit
Verify all animations from spec are implemented:
- [ ] Card hover: `transition-transform duration-150 ease-out hover:-translate-y-0.5 hover:border-l-2 hover:border-l-accent`
- [ ] Filter dropdown: `transition-all duration-[180ms] ease-out`
- [ ] Card stagger: CSS animation-delay, 40ms per card, max 8 cards (use JS index)
- [ ] CLOSING SOON chip pulse: `animate-pulse` on the status dot only
- [ ] Tab crossfade: `transition-opacity duration-[120ms]`
- [ ] Skeleton loaders: `animate-pulse bg-card rounded-lg` matching card dimensions

### 6.6 — Mobile Responsiveness Audit
Check on 375px (iPhone SE), 768px (tablet), 1280px (desktop):
- [ ] Grid collapses to single column on mobile
- [ ] FilterBar becomes scrollable horizontal strip on mobile
- [ ] Header: Submit+ button hidden on mobile (icon only or moved to menu)
- [ ] Detail page quick-stats bar wraps correctly
- [ ] All text readable without horizontal scroll

### 6.7 — Accessibility Audit
- [ ] All interactive elements have focus-visible ring: `focus-visible:ring-2 focus-visible:ring-accent`
- [ ] Color contrast: all text passes WCAG AA (verify #9E8A7A on #26150B — borderline, may need to lighten)
- [ ] All images have alt text (organizer logos: alt="{organizerName} logo")
- [ ] Apply Now button: aria-label="Apply to {hackathon.title} — opens external site"
- [ ] Filter dropdowns: aria-expanded, aria-controls
- [ ] Status chips: role="status" or aria-label for screen readers

### 6.8 — Performance Audit
- [ ] Run Lighthouse on /
- [ ] LCP < 1.5s
- [ ] No unused Tailwind classes (purge configured correctly)
- [ ] Organizer logo images: use next/image with appropriate sizes
- [ ] Fonts: preloaded in layout with `display: swap`

---

## Definition of Done
- [ ] /sitemap.xml generates all active hackathon URLs
- [ ] /robots.txt disallows /admin
- [ ] JSON-LD schema on all detail pages (validate with Google Rich Results Test)
- [ ] All animations match spec (no extra, no missing)
- [ ] Mobile layout correct at 375px
- [ ] All interactive elements keyboard-accessible
- [ ] Lighthouse performance score > 90 on directory page
