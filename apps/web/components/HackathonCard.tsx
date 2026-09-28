import Link from 'next/link'
import Image from 'next/image'
import { cn } from '@/lib/utils'
import { PrestigeBadge } from './PrestigeBadge'
import { StatusChip } from './StatusChip'
import { BookmarkButton } from './BookmarkButton'
import { RegisterButton } from './RegisterButton'
import { formatDeadline, formatPrize } from '@/lib/formatters'
import { 
  Clock, 
  MapPin, 
  Globe, 
  Trophy, 
  CheckCircle2, 
  Sparkles, 
  Cpu, 
  Coins, 
  Activity, 
  Gamepad2, 
  Leaf, 
  Compass,
  Tag
} from 'lucide-react'

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
    indiaRegion?: string | null
    description?: string | null
  }
  index?: number
  isBookmarked?: boolean
  isRegistered?: boolean
}

/**
 * Safely extract a clean display string from a theme tag.
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

/**
 * Generate category-specific ambient visuals for the Luma-style card header.
 */
function getThemeVisuals(tags: string[], title: string) {
  const combined = (tags.join(' ') + ' ' + title).toLowerCase()

  if (combined.includes('ai') || combined.includes('machine learning') || combined.includes('llm') || combined.includes('neural')) {
    return {
      gradient: 'from-[#2e1065] via-[#1e1b4b] to-[#0f172a]',
      glowColor: 'bg-violet-500/40',
      accentColor: 'text-violet-300',
      tagColor: 'text-violet-300 border-violet-500/30 bg-violet-950/60',
      Icon: Sparkles,
    }
  }
  if (combined.includes('web3') || combined.includes('crypto') || combined.includes('blockchain') || combined.includes('solana') || combined.includes('ethereum')) {
    return {
      gradient: 'from-[#042f2e] via-[#0f3d38] to-[#09151f]',
      glowColor: 'bg-teal-400/35',
      accentColor: 'text-teal-300',
      tagColor: 'text-teal-300 border-teal-500/30 bg-teal-950/60',
      Icon: Cpu,
    }
  }
  if (combined.includes('fintech') || combined.includes('finance') || combined.includes('banking') || combined.includes('payment')) {
    return {
      gradient: 'from-[#064e3b] via-[#0b3325] to-[#121c17]',
      glowColor: 'bg-emerald-400/35',
      accentColor: 'text-emerald-300',
      tagColor: 'text-emerald-300 border-emerald-500/30 bg-emerald-950/60',
      Icon: Coins,
    }
  }
  if (combined.includes('health') || combined.includes('medtech') || combined.includes('bio') || combined.includes('medical')) {
    return {
      gradient: 'from-[#083344] via-[#0c4a6e] to-[#091824]',
      glowColor: 'bg-cyan-400/35',
      accentColor: 'text-cyan-300',
      tagColor: 'text-cyan-300 border-cyan-500/30 bg-cyan-950/60',
      Icon: Activity,
    }
  }
  if (combined.includes('game') || combined.includes('gaming') || combined.includes('vr') || combined.includes('ar')) {
    return {
      gradient: 'from-[#4c0519] via-[#431407] to-[#180e1a]',
      glowColor: 'bg-rose-500/35',
      accentColor: 'text-rose-300',
      tagColor: 'text-rose-300 border-rose-500/30 bg-rose-950/60',
      Icon: Gamepad2,
    }
  }
  if (combined.includes('social') || combined.includes('climate') || combined.includes('sustainab') || combined.includes('green')) {
    return {
      gradient: 'from-[#14532d] via-[#164e2a] to-[#0a1a10]',
      glowColor: 'bg-green-400/35',
      accentColor: 'text-green-300',
      tagColor: 'text-green-300 border-green-500/30 bg-green-950/60',
      Icon: Leaf,
    }
  }

  // Default / Open Innovation / General
  return {
    gradient: 'from-[#451e0f] via-[#2c150b] to-[#140a04]',
    glowColor: 'bg-amber-500/30',
    accentColor: 'text-accent',
    tagColor: 'text-accent border-accent/30 bg-accent/10',
    Icon: Compass,
  }
}

/**
 * Format date for Luma-style calendar badge
 */
function getCalendarBadge(dateValue: Date | string | null) {
  if (!dateValue) {
    return { month: 'TBA', day: '—' }
  }
  const d = new Date(dateValue)
  if (isNaN(d.getTime())) {
    return { month: 'TBA', day: '—' }
  }
  return {
    month: d.toLocaleDateString('en-US', { month: 'short' }).toUpperCase(),
    day: d.getDate().toString(),
  }
}

export function HackathonCard({ 
  hackathon, 
  index = 0, 
  isBookmarked = false, 
  isRegistered = false 
}: HackathonCardProps) {
  const isClosed = hackathon.status === 'CLOSED'
  const rawDeadline = formatDeadline(hackathon.registrationClose)
  const calendarBadge = getCalendarBadge(hackathon.registrationClose)

  // Ensure clean date representation without "Upcoming" + "Closed" clash
  const parsedDate = hackathon.registrationClose ? new Date(hackathon.registrationClose) : null
  const formattedDateStr = parsedDate && !isNaN(parsedDate.getTime())
    ? parsedDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    : null

  let displayDeadline = rawDeadline
  if (!isClosed && (rawDeadline === 'Closed' || rawDeadline === 'Date TBA')) {
    displayDeadline = formattedDateStr ? `Closes ${formattedDateStr}` : 'Date TBA'
  }

  // Clean tags
  const cleanTags = hackathon.themeTags
    .map(safeTag)
    .filter((t) => t.length > 0 && t.length < 50)
    .slice(0, 2)

  const themeVisuals = getThemeVisuals(cleanTags, hackathon.title)
  const WatermarkIcon = themeVisuals.Icon

  // Prize calculation (Luma style)
  let prizeDisplay = 'Free Entry'
  if (hackathon.prizePool && Number(hackathon.prizePool) > 0) {
    prizeDisplay = formatPrize(hackathon.prizePool, hackathon.prizeCurrency)
  } else if (hackathon.prizeDescription) {
    prizeDisplay = hackathon.prizeDescription
  } else if (hackathon.entryFee && Number(hackathon.entryFee) > 0) {
    prizeDisplay = 'Paid Entry'
  }

  return (
    <Link
      href={`/hackathon/${hackathon.slug}`}
      aria-label={`${hackathon.title} by ${hackathon.organizerName}`}
      prefetch={true}
      className={cn(
        'group relative flex flex-col bg-[#1E1108] hover:bg-[#28170C]',
        'border border-[#4A2E18]/70 hover:border-accent/50 rounded-card overflow-hidden',
        'shadow-md hover:shadow-2xl hover:shadow-black/70',
        'transition-all duration-300 ease-out hover:-translate-y-1.5',
        isClosed && 'opacity-65',
        'opacity-0 animate-fade-in'
      )}
      style={{ animationDelay: `${Math.min(index, 7) * 80}ms` }}
    >
      {/* Visual Header / Cover Banner (Luma Style) */}
      <div className="relative w-full h-36 sm:h-40 overflow-hidden bg-[#120803] select-none border-b border-white/[0.08]">
        {/* Dynamic mesh gradient background with smooth scale on hover */}
        <div 
          className={cn(
            'absolute inset-0 bg-gradient-to-br transition-transform duration-700 ease-out group-hover:scale-105',
            themeVisuals.gradient
          )}
        >
          {/* Subtle dot matrix grid */}
          <div className="absolute inset-0 opacity-25 bg-[radial-gradient(#ffffff25_1px,transparent_1px)] [background-size:14px_14px]" />
          
          {/* Ambient luminous orb */}
          <div 
            className={cn(
              'absolute -top-10 -right-10 w-44 h-44 rounded-full blur-2xl transition-opacity duration-500 opacity-60 group-hover:opacity-90',
              themeVisuals.glowColor
            )} 
          />

          {/* Watermark Category Glyph */}
          <div className="absolute -bottom-4 -right-2 text-white/[0.08] group-hover:text-white/[0.15] transition-all duration-500 transform rotate-12 group-hover:rotate-6 group-hover:scale-110">
            <WatermarkIcon className="w-28 h-28 stroke-[1.2]" />
          </div>

          {/* Vignette bottom shadow to blend seamlessly */}
          <div className="absolute inset-0 bg-gradient-to-t from-[#1E1108]/90 via-transparent to-black/25" />
        </div>

        {/* Signature Luma Calendar Badge (Top-Left) */}
        <div className="absolute top-3 left-3 z-10 flex flex-col items-center justify-center min-w-[50px] px-2.5 py-1.5 rounded-xl bg-black/80 backdrop-blur-md border border-white/20 shadow-lg group-hover:border-white/35 transition-colors">
          <span className="text-[10px] font-mono font-bold tracking-widest text-accent uppercase leading-none">
            {calendarBadge.month}
          </span>
          <span className="text-lg font-mono font-bold text-white leading-none mt-1">
            {calendarBadge.day}
          </span>
        </div>

        {/* Top-Right Floating Controls: Prestige + Register + Bookmark */}
        <div className="absolute top-3 right-3 z-20 flex items-center gap-1.5">
          <PrestigeBadge tier={hackathon.prestigeTier} />
          <RegisterButton hackathonId={hackathon.id} initialRegistered={isRegistered} />
          <BookmarkButton hackathonId={hackathon.id} initialBookmarked={isBookmarked} />
        </div>
      </div>

      {/* Card Content (Body) */}
      <div className="p-4 sm:p-5 flex flex-col flex-1 justify-between gap-3 relative z-10">
        <div className="flex flex-col gap-2.5">
          {/* Subtitle row: Status + Time indicator */}
          <div className="flex items-center justify-between gap-2 text-xs">
            <StatusChip status={hackathon.status} />
            {!isClosed && (
              <span className="font-mono text-text-muted flex items-center gap-1 text-[11px]">
                <Clock className="w-3 h-3 text-text-muted/70" />
                {displayDeadline}
              </span>
            )}
          </div>

          {/* Event Title */}
          <h3 className="font-sans font-bold text-base sm:text-[17px] text-white leading-snug line-clamp-2 min-h-[2.6rem] group-hover:text-accent transition-colors duration-200">
            {hackathon.title}
          </h3>

          {/* Host / Organizer Row (Classic Luma presentation) */}
          <div className="flex items-center justify-between text-xs text-text-muted pt-0.5">
            <div className="flex items-center gap-2 min-w-0">
              {hackathon.organizerLogoUrl ? (
                <Image
                  src={hackathon.organizerLogoUrl}
                  alt={hackathon.organizerName}
                  width={20}
                  height={20}
                  className="rounded-full ring-1 ring-white/10 flex-shrink-0"
                />
              ) : (
                <div className="w-5 h-5 rounded-full bg-gradient-to-br from-amber-600 to-indigo-600 flex items-center justify-center text-[10px] font-bold text-white shadow-sm ring-1 ring-white/15 flex-shrink-0">
                  {hackathon.organizerName[0]?.toUpperCase() || 'H'}
                </div>
              )}
              <div className="flex items-center gap-1.5 min-w-0">
                <span className="text-text-muted/80">By</span>
                <span className="font-semibold text-text-primary truncate">
                  {hackathon.organizerName}
                </span>
                {(hackathon.prestigeTier === 'T1' || hackathon.prestigeTier === 'T2') && (
                  <CheckCircle2 className="w-3.5 h-3.5 text-accent flex-shrink-0 inline-block" />
                )}
              </div>
            </div>

            {/* Scope Flag */}
            <span 
              className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-white/[0.05] border border-white/10 text-text-muted flex-shrink-0"
              title={hackathon.scope === 'GLOBAL' ? 'Global Event' : 'India Event'}
            >
              {hackathon.scope === 'GLOBAL' ? '🌐 Global' : '🇮🇳 India'}
            </span>
          </div>

          {/* Location / Mode */}
          <div className="flex items-center gap-1.5 text-xs text-text-muted/90 font-sans">
            {hackathon.mode === 'OFFLINE' ? (
              <>
                <MapPin className="w-3.5 h-3.5 text-text-muted/70 flex-shrink-0" />
                <span className="truncate">{hackathon.indiaRegion || 'In-Person'}</span>
              </>
            ) : hackathon.mode === 'HYBRID' ? (
              <>
                <MapPin className="w-3.5 h-3.5 text-text-muted/70 flex-shrink-0" />
                <span className="truncate">{hackathon.indiaRegion ? `${hackathon.indiaRegion} / Hybrid` : 'Hybrid'}</span>
              </>
            ) : (
              <>
                <Globe className="w-3.5 h-3.5 text-text-muted/70 flex-shrink-0" />
                <span>Virtual / Online</span>
              </>
            )}
          </div>
        </div>

        {/* Footer Meta: Prize Pool Pill + Category Tags */}
        <div className="pt-3 border-t border-[#4A2E18]/60 flex items-center justify-between gap-2">
          {/* Prize pool badge */}
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/[0.06] border border-white/15 text-xs font-mono font-medium text-text-primary">
            {prizeDisplay.includes('Free') ? (
              <Tag className="w-3.5 h-3.5 text-emerald-400" />
            ) : (
              <Trophy className="w-3.5 h-3.5 text-amber-400" />
            )}
            <span className="truncate">{prizeDisplay}</span>
          </div>

          {/* Category tags */}
          <div className="flex items-center gap-1.5 flex-wrap justify-end">
            {cleanTags.map((tag) => (
              <span
                key={tag}
                className={cn(
                  'px-2.5 py-0.5 rounded-full text-[11px] font-mono border truncate max-w-[110px]',
                  themeVisuals.tagColor
                )}
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>
    </Link>
  )
}
