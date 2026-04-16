import { notFound } from 'next/navigation'
import type { Metadata } from 'next'
import { prisma } from '@/lib/db'
import { PrestigeBadge } from '@/components/PrestigeBadge'
import { StatusChip } from '@/components/StatusChip'
import { formatDeadline, formatPrize, formatFee } from '@/lib/formatters'

export async function generateStaticParams() {
  try {
    const hackathons = await prisma.hackathon.findMany({
      select: { slug: true },
      where: { status: { not: 'CLOSED' } },
    })
    return hackathons.map((hackathon) => ({ slug: hackathon.slug }))
  } catch (error) {
    console.error('Failed to generate static hackathon params:', error)
    return []
  }
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>
}): Promise<Metadata> {
  const { slug } = await params
  const h = await prisma.hackathon
    .findUnique({
      where: { slug: slug },
      select: { title: true, description: true, organizerName: true },
    })
    .catch((error) => {
      console.error(`Failed to generate metadata for hackathon slug "${slug}":`, error)
      return null
    })
  if (!h) return {}
  return {
    title: `${h.title} — ${h.organizerName} | 1ph`,
    description: h.description,
    openGraph: {
      title: h.title,
      description: h.description,
      images: [`/api/og?slug=${slug}`],
    },
  }
}

const MODE_MAP = { ONLINE: 'Online', OFFLINE: 'In-Person', HYBRID: 'Hybrid' }
const ELIGIBILITY_MAP = { STUDENTS: 'Students only', OPEN: 'Open to all', PROFESSIONALS: 'Working professionals' }
const DURATION_MAP = { HR24: '24 hours', HR48: '48 hours', WEEK: 'Week-long', MONTH: 'Month-long', CUSTOM: 'Custom' }

export default async function HackathonDetailPage({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  const h = await prisma.hackathon.findUnique({ where: { slug: slug } })
  if (!h) notFound()

  const isClosed = h.status === 'CLOSED'
  const prize = h.prizeDescription ?? formatPrize(h.prizePool ? Number(h.prizePool) : null, h.prizeCurrency)
  const fee = formatFee(h.entryFee ? Number(h.entryFee) : null, h.entryFeeCurrency)
  const deadline = formatDeadline(h.registrationClose)

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
              <img src={h.organizerLogoUrl} alt={`${h.organizerName} logo`} className="w-8 h-8 rounded object-contain" />
            ) : (
              <div className="w-8 h-8 rounded bg-tag-bg flex items-center justify-center">
                <span className="text-accent font-mono font-bold text-sm">{h.organizerName.charAt(0)}</span>
              </div>
            )}
            <span className="font-mono text-sm text-text-muted">{h.organizerName}</span>
            <PrestigeBadge tier={h.prestigeTier} />
            <span className="ml-auto text-lg" aria-label={h.scope === 'GLOBAL' ? 'Global' : 'India'}>
              {h.scope === 'GLOBAL' ? '🌐' : '🇮🇳'}
            </span>
          </div>

          <h1 className="font-serif text-3xl md:text-4xl text-text-primary leading-tight mb-4">
            {h.title}
          </h1>

          {/* Status + deadline */}
          <div className="flex items-center gap-4">
            <StatusChip status={h.status} />
            {!isClosed && (
              <span className="font-mono text-sm text-text-muted">
                Registration closes {deadline}
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
          ].map(stat => (
            <div key={stat.label} className="bg-card border border-border rounded-card p-3">
              <div className="font-mono text-xs text-text-muted mb-1">{stat.label}</div>
              <div className="font-mono text-sm text-text-primary font-medium">{stat.value}</div>
            </div>
          ))}
        </div>

        {/* Apply CTA */}
        <div>
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
              className="block w-full py-3 rounded-card bg-accent text-bg font-mono font-medium text-center text-sm hover:bg-accent/90 transition-colors duration-150 focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-bg"
              aria-label={`Apply to ${h.title} — opens external site`}
            >
              Apply Now →
            </a>
          )}
        </div>

        {/* Description */}
        <div>
          <h2 className="font-serif text-xl text-text-primary mb-2">About</h2>
          <p className="font-sans text-text-muted text-sm leading-relaxed">
            {h.longDescription ?? h.description}
          </p>
        </div>

        {/* Eligibility */}
        <div>
          <h2 className="font-serif text-xl text-text-primary mb-2">Eligibility</h2>
          <p className="font-mono text-sm text-text-muted">{ELIGIBILITY_MAP[h.eligibility]}</p>
          {h.teamSizeMax ? (
            <p className="font-mono text-sm text-text-muted mt-1">
              Team size: {h.teamSizeMin}–{h.teamSizeMax} members
            </p>
          ) : (
            <p className="font-mono text-sm text-text-muted mt-1">
              Team size: {h.teamSizeMin}+ members
            </p>
          )}
        </div>

        {/* Theme tags */}
        {h.themeTags.length > 0 && (
          <div>
            <h2 className="font-serif text-xl text-text-primary mb-2">Themes</h2>
            <div className="flex flex-wrap gap-2">
              {h.themeTags.map(tag => (
                <span key={tag} className="px-3 py-1 bg-tag-bg border border-border rounded-chip font-mono text-xs text-accent/80">
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Sponsors */}
        {h.sponsors.length > 0 && (
          <div>
            <h2 className="font-serif text-xl text-text-primary mb-2">Sponsors</h2>
            <div className="flex flex-wrap gap-2">
              {h.sponsors.map(s => (
                <span key={s} className="px-3 py-1 bg-card border border-border rounded-chip font-mono text-xs text-text-muted">
                  {s}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="pt-4 border-t border-border flex items-center justify-between">
          <span className="font-mono text-xs text-text-muted">
            Listed from {h.source.charAt(0) + h.source.slice(1).toLowerCase().replace('_', ' ')}
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
