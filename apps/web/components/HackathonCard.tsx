import Link from 'next/link'
import Image from 'next/image'
import { cn } from '@/lib/utils'
import { PrestigeBadge } from './PrestigeBadge'
import { StatusChip } from './StatusChip'
import { formatDeadline, formatPrize, formatFee } from '@/lib/formatters'

interface HackathonCardProps {
  hackathon: {
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
    registrationClose: Date | string
    mode: 'ONLINE' | 'OFFLINE' | 'HYBRID'
    themeTags: string[]
    scope: 'GLOBAL' | 'INDIA'
  }
  index?: number
}

const MODE_LABEL: Record<string, string> = {
  ONLINE:  'Online',
  OFFLINE: 'In-Person',
  HYBRID:  'Hybrid',
}

export function HackathonCard({ hackathon, index = 0 }: HackathonCardProps) {
  const isClosed = hackathon.status === 'CLOSED'
  const deadline = formatDeadline(hackathon.registrationClose)

  return (
    <Link
      href={`/hackathon/${hackathon.slug}`}
      className={cn(
        'group block bg-card border border-border rounded-card p-5',
        'transition-all duration-150 ease-out',
        'hover:-translate-y-0.5 hover:border-l-2 hover:border-l-accent hover:shadow-lg',
        isClosed && 'opacity-60 pointer-events-none',
        'opacity-0 animate-fade-in'
      )}
      style={{ animationDelay: `${Math.min(index, 7) * 40}ms` }}
      aria-label={`${hackathon.title} by ${hackathon.organizerName}`}
    >
      {/* Top row: org + scope */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2 min-w-0">
          {hackathon.organizerLogoUrl ? (
            <Image
              src={hackathon.organizerLogoUrl}
              alt={`${hackathon.organizerName} logo`}
              width={24}
              height={24}
              className="w-6 h-6 rounded-sm object-contain flex-shrink-0"
            />
          ) : (
            <div className="w-6 h-6 rounded-sm bg-tag-bg flex items-center justify-center flex-shrink-0">
              <span className="text-accent text-xs font-mono font-bold">
                {hackathon.organizerName.charAt(0).toUpperCase()}
              </span>
            </div>
          )}
          <span className="text-text-muted text-xs font-mono truncate">
            {hackathon.organizerName}
          </span>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0">
          <span className="text-sm" aria-label={hackathon.scope === 'GLOBAL' ? 'Global hackathon' : 'India hackathon'}>
            {hackathon.scope === 'GLOBAL' ? '🌐' : '🇮🇳'}
          </span>
          <PrestigeBadge tier={hackathon.prestigeTier} />
        </div>
      </div>

      {/* Title */}
      <h2 className="font-serif text-lg leading-tight text-text-primary mb-3 line-clamp-2">
        {hackathon.title}
      </h2>

      {/* Status + deadline row */}
      <div className="flex items-center justify-between mb-4">
        <StatusChip status={hackathon.status} />
        {!isClosed && (
          <span
            className="text-xs font-mono text-text-muted"
            title={new Date(hackathon.registrationClose).toLocaleDateString('en-IN', {
              day: 'numeric', month: 'short', year: 'numeric'
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
            {hackathon.prizeDescription ?? formatPrize(hackathon.prizePool, hackathon.prizeCurrency)}
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

      {/* Mode + tags row */}
      <div className="flex items-center gap-2 flex-wrap">
        <span className="px-2 py-0.5 bg-tag-bg rounded-chip text-xs font-mono text-text-muted border border-border">
          {MODE_LABEL[hackathon.mode]}
        </span>
        {hackathon.themeTags.slice(0, 2).map(tag => (
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
