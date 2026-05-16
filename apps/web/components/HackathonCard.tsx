import Link from 'next/link'
import Image from 'next/image'
import { cn } from '@/lib/utils'
import { PrestigeBadge } from './PrestigeBadge'
import { StatusChip } from './StatusChip'
import { BookmarkButton } from './BookmarkButton'
import { RegisterButton } from './RegisterButton'
import { formatDeadline, formatPrize, formatFee } from '@/lib/formatters'

interface HackathonCardProps {
  hackathon: {
    id: string
    slug: string
    title: string
    organizerName: string
    organizerLogoUrl?: string | null
    prestigeTier: 'T1' | 'T2' | 'T3'
    status: 'UPCOMING' | 'OPEN' | 'CLOSING_SOON' | 'CLOSED'
    prizePool?: number | null
    prizeCurrency?: string | null
    prizeDescription?: string | null
    entryFee?: number | null
    entryFeeCurrency?: string | null
    registrationClose: Date | string | null
    mode: 'ONLINE' | 'OFFLINE' | 'HYBRID'
    themeTags: string[]
    scope: 'GLOBAL' | 'INDIA'
    description?: string | null
  }
  index?: number
  isBookmarked?: boolean
  isRegistered?: boolean
}

const MODE_LABEL: Record<string, string> = {
  ONLINE: 'Online',
  OFFLINE: 'In-Person',
  HYBRID: 'Hybrid',
}

/**
 * Safely extract a display string from a theme tag.
 * Devfolio (and some other sources) occasionally store tags as raw JSON/dict strings
 * e.g. "{'name': 'FinTech', 'verified': True, 'uuid': '...'}"
 * This strips them down to just the name.
 */
function safeTag(tag: string): string {
  if (!tag) return ''
  if (tag.startsWith('{') || tag.startsWith("{'")) {
    try {
      const normalized = tag.replace(/'/g, '"').replace(/True/g, 'true').replace(/False/g, 'false')
      const parsed = JSON.parse(normalized)
      return (parsed.name || parsed.label || parsed.title || '').trim()
    } catch {
      const match = tag.match(/['"]name['"]\s*:\s*['"]([^'"]+)['"]/)
      return match ? match[1].trim() : ''
    }
  }
  return tag.trim()
}

export function HackathonCard({ hackathon, index = 0, isBookmarked = false, isRegistered = false }: HackathonCardProps) {
  const isClosed = hackathon.status === 'CLOSED'
  const deadline = formatDeadline(hackathon.registrationClose)

  // Sanitize tags — remove raw JSON objects and empty strings
  const cleanTags = hackathon.themeTags
    .map(safeTag)
    .filter((t) => t.length > 0 && t.length < 60)
    .slice(0, 2)

  return (
    <Link
      href={`/hackathon/${hackathon.slug}`}
      aria-label={`${hackathon.title} by ${hackathon.organizerName}`}
      prefetch={true}
      className={cn(
        'group relative block bg-card border border-border rounded-card p-5',
        'transition-all duration-500 ease-effortless',
        'hover:-translate-y-1 hover:border-l-2 hover:border-l-accent hover:shadow-2xl hover:bg-card/80',
        isClosed && 'opacity-60 pointer-events-none',
        'opacity-0 animate-fade-in'
      )}
      style={{ animationDelay: `${Math.min(index, 7) * 100}ms` }}
    >
      {/* Top row: org + scope + tier */}
      <div className="relative z-10 flex items-center justify-between mb-3">
        <div className="flex items-center gap-2 min-w-0">
          {hackathon.organizerLogoUrl ? (
            <Image
              src={hackathon.organizerLogoUrl}
              alt={hackathon.organizerName}
              width={20}
              height={20}
              className="rounded-full grayscale group-hover:grayscale-0 transition-all duration-500"
            />
          ) : (
            <div className="w-5 h-5 bg-tag-bg rounded-full flex items-center justify-center text-[10px] font-bold">
              {hackathon.organizerName[0]}
            </div>
          )}
          <span className="text-text-muted text-xs font-mono truncate">{hackathon.organizerName}</span>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0 relative z-20">
          <span
            className="text-sm"
            aria-label={hackathon.scope === 'GLOBAL' ? 'Global hackathon' : 'India hackathon'}
          >
            {hackathon.scope === 'GLOBAL' ? '🌐' : '🇮🇳'}
          </span>
          <PrestigeBadge tier={hackathon.prestigeTier} />
          <RegisterButton hackathonId={hackathon.id} initialRegistered={isRegistered} />
          <BookmarkButton hackathonId={hackathon.id} initialBookmarked={isBookmarked} />
        </div>
      </div>

      {/* Title */}
      <h3 className="relative z-10 text-lg font-serif text-text-primary leading-tight mb-4 group-hover:text-accent transition-colors duration-500 line-clamp-2 min-h-[3.5rem]">
        {hackathon.title}
      </h3>

      {/* Description preview */}
      {hackathon.description && (
        <p className="font-sans text-xs text-text-muted mb-3 line-clamp-2 leading-relaxed">
          {hackathon.description}
        </p>
      )}

      {/* Status + deadline */}
      <div className="flex items-center justify-between mb-4">
        <StatusChip status={hackathon.status} />
        {!isClosed && (
          <span
            className="text-xs font-mono text-text-muted"
            title={new Date(hackathon.registrationClose).toLocaleDateString('en-IN', {
              day: 'numeric',
              month: 'short',
              year: 'numeric',
            })}
          >
            {deadline}
          </span>
        )}
      </div>

      {/* Stats row */}
      <div className="flex items-center gap-3 mb-4 text-xs font-mono">
        <div className="flex flex-col gap-0.5">
          <span className="text-text-muted">Prize</span>
          <span className="text-text-primary font-medium">
            {hackathon.prizeDescription || formatPrize(hackathon.prizePool, hackathon.prizeCurrency)}
          </span>
        </div>
        <div className="w-px h-6 bg-border" />
        <div className="flex flex-col gap-0.5">
          <span className="text-text-muted">Entry</span>
          <span className="text-text-primary font-medium">
            {formatFee(hackathon.entryFee, hackathon.entryFeeCurrency)}
          </span>
        </div>
      </div>

      {/* Mode + tags */}
      <div className="flex items-center gap-2 flex-wrap">
        <span className="px-2 py-0.5 bg-tag-bg rounded-chip text-xs font-mono text-text-muted border border-border">
          {MODE_LABEL[hackathon.mode]}
        </span>
        {cleanTags.map((tag) => (
          <span
            key={tag}
            className="px-2 py-0.5 bg-tag-bg rounded-chip text-xs font-mono text-accent/80 border border-border"
          >
            {tag}
          </span>
        ))}
      </div>
    </Link>
  )
}
