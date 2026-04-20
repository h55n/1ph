import { notFound } from 'next/navigation'
import type { Metadata } from 'next'
import { prisma } from '@/lib/db'
import { PrestigeBadge } from '@/components/PrestigeBadge'
import { StatusChip } from '@/components/StatusChip'
import { BookmarkButton } from '@/components/BookmarkButton'
import { formatDeadline, formatPrize, formatFee } from '@/lib/formatters'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'

export const revalidate = 1800
export const dynamicParams = true

export async function generateStaticParams() {
  const rows = await prisma.hackathon
    .findMany({
      where: { status: { in: ['OPEN', 'CLOSING_SOON', 'UPCOMING'] } },
      select: { slug: true },
      orderBy: { registrationClose: 'asc' },
      take: 500,
    })
    .catch(() => [])
  return rows.map((row) => ({ slug: row.slug }))
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params
  const h = await prisma.hackathon
    .findUnique({
      where: { slug },
      select: { title: true, description: true, longDescription: true, organizerName: true },
    })
    .catch(() => null)
  if (!h) return {}
  const desc = h.longDescription || h.description
  return {
    title: `${h.title} — ${h.organizerName} | 1ph`,
    description: desc?.slice(0, 160),
    openGraph: {
      title: h.title,
      description: desc?.slice(0, 160),
      images: [`/api/og?slug=${slug}`],
    },
  }
}

const MODE_MAP = { ONLINE: 'Online', OFFLINE: 'In-Person', HYBRID: 'Hybrid' }
const ELIGIBILITY_MAP = { STUDENTS: 'Students only', OPEN: 'Open to all', PROFESSIONALS: 'Working professionals' }
const DURATION_MAP = { HR24: '24 hours', HR48: '48 hours', WEEK: 'Week-long', MONTH: 'Month-long', CUSTOM: 'Custom duration' }

/** Safely parse a theme tag that might be a raw JSON string or object */
function safeTag(tag: string): string {
  if (!tag) return ''
  // If it looks like a dict/JSON (Devfolio sometimes stores raw objects as strings)
  if (tag.startsWith('{') || tag.startsWith("{'")) {
    try {
      // Handle Python-style dicts with single quotes
      const normalized = tag.replace(/'/g, '"').replace(/True/g, 'true').replace(/False/g, 'false')
      const parsed = JSON.parse(normalized)
      return parsed.name || parsed.label || parsed.title || ''
    } catch {
      // Try extracting name= or 'name': pattern
      const match = tag.match(/['"']name['"']\s*:\s*['"']([^'"']+)['"']/)
      if (match) return match[1]
      return ''
    }
  }
  return tag
}

export default async function HackathonDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  const h = await prisma.hackathon.findUnique({ where: { slug } })
  if (!h) notFound()

  const session = await getServerSession(authOptions)
  const userId = (session?.user as { id?: string })?.id

  let isBookmarked = false
  if (userId) {
    const bm = await prisma.bookmark
      .findUnique({
        where: { userId_hackathonId: { userId, hackathonId: h.id } },
      })
      .catch(() => null)
    isBookmarked = !!bm
  }

  const isClosed = h.status === 'CLOSED'
  const prize = h.prizeDescription ?? formatPrize(h.prizePool ? Number(h.prizePool) : null, h.prizeCurrency)
  const fee = formatFee(h.entryFee ? Number(h.entryFee) : null, h.entryFeeCurrency)
  const deadline = formatDeadline(h.registrationClose)

  // Sanitize theme tags — strip raw JSON objects
  const cleanTags = h.themeTags
    .map(safeTag)
    .filter((t) => t.length > 0 && t.length < 60)

  // Build a rich About text
  const aboutText = h.longDescription || h.description || ''
  // Split into paragraphs if it has sentence breaks
  const aboutParagraphs = aboutText
    .split(/\n\n|\. (?=[A-Z])/)
    .map((p) => p.trim())
    .filter((p) => p.length > 10)

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Event',
    name: h.title,
    startDate: h.eventStart.toISOString(),
    endDate: h.eventEnd?.toISOString(),
    eventStatus: isClosed
      ? 'https://schema.org/EventCancelled'
      : 'https://schema.org/EventScheduled',
    eventAttendanceMode:
      h.mode === 'ONLINE'
        ? 'https://schema.org/OnlineEventAttendanceMode'
        : 'https://schema.org/OfflineEventAttendanceMode',
    location:
      h.mode === 'ONLINE'
        ? { '@type': 'VirtualLocation', url: h.applyUrl }
        : { '@type': 'Place', name: h.indiaRegion ?? 'TBD' },
    organizer: { '@type': 'Organization', name: h.organizerName },
    offers: {
      '@type': 'Offer',
      price: h.entryFee ? Number(h.entryFee) : 0,
      priceCurrency: h.entryFeeCurrency ?? 'USD',
      url: h.applyUrl,
    },
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      <div className="max-w-2xl mx-auto space-y-8 pt-4">
        {/* Header */}
        <div>
          <div className="flex items-center gap-3 mb-3">
            {h.organizerLogoUrl ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={h.organizerLogoUrl}
                alt={`${h.organizerName} logo`}
                className="w-8 h-8 rounded object-contain"
              />
            ) : (
              <div className="w-8 h-8 rounded bg-tag-bg flex items-center justify-center">
                <span className="text-accent font-mono font-bold text-sm">
                  {h.organizerName.charAt(0)}
                </span>
              </div>
            )}
            <span className="font-mono text-sm text-text-muted">{h.organizerName}</span>
            <PrestigeBadge tier={h.prestigeTier} />
            <span className="ml-auto flex items-center gap-2">
              <span
                className="text-lg"
                aria-label={h.scope === 'GLOBAL' ? 'Global' : 'India'}
              >
                {h.scope === 'GLOBAL' ? '🌐' : '🇮🇳'}
              </span>
              <BookmarkButton hackathonId={h.id} initialBookmarked={isBookmarked} />
            </span>
          </div>

          <h1 className="font-serif text-3xl md:text-4xl text-text-primary leading-tight mb-4">
            {h.title}
          </h1>

          <div className="flex items-center gap-4 flex-wrap">
            <StatusChip status={h.status} />
            {!isClosed && (
              <span className="font-mono text-sm text-text-muted">
                Registration closes {deadline}
              </span>
            )}
            {isClosed && h.eventStart && (
              <span className="font-mono text-xs text-text-muted">
                Ended {new Date(h.eventStart).toLocaleDateString('en-IN', { month: 'short', year: 'numeric' })}
              </span>
            )}
          </div>
        </div>

        {/* Quick stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { label: 'Prize', value: prize },
            { label: 'Entry', value: fee },
            { label: 'Mode', value: MODE_MAP[h.mode] },
            { label: 'Duration', value: DURATION_MAP[h.durationType] },
          ].map((stat) => (
            <div key={stat.label} className="bg-card border border-border rounded-card p-3">
              <div className="font-mono text-xs text-text-muted mb-1">{stat.label}</div>
              <div className="font-mono text-sm text-text-primary font-medium">{stat.value}</div>
            </div>
          ))}
        </div>

        {/* Apply CTA */}
        {isClosed ? (
          <button
            disabled
            className="w-full py-3 rounded-card bg-card border border-border text-text-muted font-mono text-sm cursor-not-allowed"
          >
            Registration Closed
          </button>
        ) : (
          <a
            href={h.applyUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="block w-full py-3 rounded-card bg-accent text-bg font-mono font-medium text-center text-sm hover:bg-accent/90 transition-colors duration-150"
            aria-label={`Apply to ${h.title} — opens external site`}
          >
            Apply Now →
          </a>
        )}

        {/* About — rich, multi-paragraph */}
        <div>
          <h2 className="font-serif text-xl text-text-primary mb-3">About</h2>
          {aboutParagraphs.length > 1 ? (
            <div className="space-y-3">
              {aboutParagraphs.map((para, i) => (
                <p key={i} className="font-sans text-text-muted text-sm leading-relaxed">
                  {para.endsWith('.') ? para : `${para}.`}
                </p>
              ))}
            </div>
          ) : (
            <p className="font-sans text-text-muted text-sm leading-relaxed">
              {aboutText ||
                `${h.title} is a hackathon organised by ${h.organizerName}. Join builders, designers, and creators to compete, collaborate, and build something meaningful.`}
            </p>
          )}

          {/* Key details chips below About */}
          <div className="flex flex-wrap gap-2 mt-4">
            <span className="px-3 py-1 bg-tag-bg border border-border rounded-chip font-mono text-xs text-text-muted">
              {MODE_MAP[h.mode]}
            </span>
            <span className="px-3 py-1 bg-tag-bg border border-border rounded-chip font-mono text-xs text-text-muted">
              {ELIGIBILITY_MAP[h.eligibility]}
            </span>
            <span className="px-3 py-1 bg-tag-bg border border-border rounded-chip font-mono text-xs text-text-muted">
              Team: {h.teamSizeMin}{h.teamSizeMax ? `–${h.teamSizeMax}` : '+'} members
            </span>
            {h.scope === 'INDIA' && (
              <span className="px-3 py-1 bg-tag-bg border border-border rounded-chip font-mono text-xs text-accent/80">
                🇮🇳 India
              </span>
            )}
          </div>
        </div>

        {/* Dates */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {h.registrationOpen && (
            <div className="bg-card border border-border rounded-card p-3">
              <div className="font-mono text-xs text-text-muted mb-1">Registration Opens</div>
              <div className="font-mono text-sm text-text-primary">
                {new Date(h.registrationOpen).toLocaleDateString('en-IN', {
                  day: 'numeric', month: 'short', year: 'numeric',
                })}
              </div>
            </div>
          )}
          <div className="bg-card border border-border rounded-card p-3">
            <div className="font-mono text-xs text-text-muted mb-1">
              {isClosed ? 'Registration Closed' : 'Registration Deadline'}
            </div>
            <div className={`font-mono text-sm ${isClosed ? 'text-text-muted' : 'text-closing'}`}>
              {new Date(h.registrationClose).toLocaleDateString('en-IN', {
                day: 'numeric', month: 'short', year: 'numeric',
              })}
            </div>
          </div>
          {h.eventStart && (
            <div className="bg-card border border-border rounded-card p-3">
              <div className="font-mono text-xs text-text-muted mb-1">Event Start</div>
              <div className="font-mono text-sm text-text-primary">
                {new Date(h.eventStart).toLocaleDateString('en-IN', {
                  day: 'numeric', month: 'short', year: 'numeric',
                })}
              </div>
            </div>
          )}
          {h.eventEnd && (
            <div className="bg-card border border-border rounded-card p-3">
              <div className="font-mono text-xs text-text-muted mb-1">Event End</div>
              <div className="font-mono text-sm text-text-primary">
                {new Date(h.eventEnd).toLocaleDateString('en-IN', {
                  day: 'numeric', month: 'short', year: 'numeric',
                })}
              </div>
            </div>
          )}
        </div>

        {/* Theme tags — only shown if clean tags exist */}
        {cleanTags.length > 0 && (
          <div>
            <h2 className="font-serif text-xl text-text-primary mb-3">Themes & Tracks</h2>
            <div className="flex flex-wrap gap-2">
              {cleanTags.map((tag) => (
                <span
                  key={tag}
                  className="px-3 py-1 bg-tag-bg border border-border rounded-chip font-mono text-xs text-accent/80"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Sponsors */}
        {h.sponsors.length > 0 && (
          <div>
            <h2 className="font-serif text-xl text-text-primary mb-3">Sponsors</h2>
            <div className="flex flex-wrap gap-2">
              {h.sponsors.map((s) => (
                <span
                  key={s}
                  className="px-3 py-1 bg-card border border-border rounded-chip font-mono text-xs text-text-muted"
                >
                  {s}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="pt-4 border-t border-border flex items-center justify-between flex-wrap gap-2">
          <span className="font-mono text-xs text-text-muted">
            Listed from{' '}
            {h.source.charAt(0) + h.source.slice(1).toLowerCase().replace('_', ' ')}
            {h.isVerified && ' · ✓ Verified'}
          </span>
          <a
            href={`mailto:hello@1ph.dev?subject=Issue with: ${h.title}`}
            className="font-mono text-xs text-text-muted hover:text-accent transition-colors"
          >
            Report an issue
          </a>
        </div>
      </div>
    </>
  )
}
