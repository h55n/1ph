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
  Compass 
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
      gradient: 'from-[#1e1b4b] via-[#2d124d] to-[#0f172a]',
      glowColor: 'bg-indigo-500/25',
      accentColor: 'text-indigo-300',
      tagColor: 'text-indigo-300/90 border-indigo-500/20 bg-indigo-950/40',
      Icon: Sparkles,
    }
  }
  if (combined.includes('web3') || combined.includes('crypto') || combined.includes('blockchain') || combined.includes('solana') || combined.includes('ethereum')) {
    return {
      gradient: 'from-[#042f2e] via-[#0f3d38] to-[#0b1520]',
      glowColor: 'bg-teal-400/20',
      accentColor: 'text-teal-300',
      tagColor: 'text-teal-300/90 border-teal-500/20 bg-teal-950/40',
      Icon: Cpu,
    }
  }
  if (combined.includes('fintech') || combined.includes('finance') || combined.includes('banking') || combined.includes('payment')) {
    return {
      gradient: 'from-[#064e3b] via-[#103b2c] to-[#141d18]',
      glowColor: 'bg-emerald-400/20',
      accentColor: 'text-emerald-300',
      tagColor: 'text-emerald-300/90 border-emerald-500/20 bg-emerald-950/40',
      Icon: Coins,
    }
  }
  if (combined.includes('health') || combined.includes('medtech') || combined.includes('bio') || combined.includes('medical')) {
    return {
      gradient: 'from-[#083344] via-[#0e485e] to-[#0c1924]',
      glowColor: 'bg-cyan-400/20',
      accentColor: 'text-cyan-300',
      tagColor: 'text-cyan-300/90 border-cyan-500/20 bg-cyan-950/40',
      Icon: Activity,
    }
  }
  if (combined.includes('game') || combined.includes('gaming') || combined.includes('vr') || combined.includes('ar')) {
    return {
      gradient: 'from-[#4c0519] via-[#4a1240] to-[#181120]',
      glowColor: 'bg-rose-500/20',
      accentColor: 'text-rose-300',
      tagColor: 'text-rose-300/90 border-rose-500/20 bg-rose-950/40',
      Icon: Gamepad2,
    }
  }
  if (combined.includes('social') || combined.includes('climate') || combined.includes('sustainab') || combined.includes('green')) {
    return {
      gradient: 'from-[#14532d] via-[#164627] to-[#0e1d13]',
      glowColor: 'bg-green-400/20',
      accentColor: 'text-green-300',
      tagColor: 'text-green-300/90 border-green-500/20 bg-green-950/40',
      Icon: Leaf,
    }
  }

  // Default / Open Innovation / General
  return {
    gradient: 'from-[#3b1c0e] via-[#2a140a] to-[#140b05]',
    glowColor: 'bg-amber-500/15',
    accentColor: 'text-accent',
    tagColor: 'text-accent/90 border-accent/20 bg-accent/5',
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
  const deadline = formatDeadline(hackathon.registrationClose)
  const calendarBadge = getCalendarBadge(hackathon.registrationClose)

  // Clean tags
  const cleanTags = hackathon.themeTags
    .map(safeTag)
    .filter((t) => t.length > 0 && t.length < 50)
    .slice(0, 2)

  const themeVisuals = getThemeVisuals(cleanTags, hackathon.title)
  const WatermarkIcon = themeVisuals.Icon

  // Prize calculation
  const prizeDisplay = hackathon.prizeDescription 
    || formatPrize(hackathon.prizePool, hackathon.prizeCurrency) 
    || (hackathon.entryFee ? 'Paid' : 'Free Entry')

  return (
    <Link
      href={`/hackathon/${hackathon.slug}`}
      aria-label={`${hackathon.title} by ${hackathon.organizerName}`}
      prefetch={true}
      className={cn(
        'group relative flex flex-col bg-[#27150A]/90 hover:bg-[#321B0E]',
        'border border-[#4A2E18]/70 hover:border-accent/40 rounded-card overflow-hidden',
        'shadow-md hover:shadow-2xl hover:shadow-black/60',
        'transition-all duration-300 ease-out hover:-translate-y-1.5',
        isClosed && 'opacity-65',
        'opacity-0 animate-fade-in'
      )}
      style={{ animationDelay: `${Math.min(index, 7) * 80}ms` }}
    >
      {/* Visual Header / Cover Banner (Luma Style) */}
      <div className="relative w-full h-36 sm:h-40 overflow-hidden bg-[#160a04] select-none">
        {/* Dynamic mesh gradient background with smooth scale on hover */}
        <div 
          className={cn(
            'absolute inset-0 bg-gradient-to-br transition-transform duration-700 ease-out group-hover:scale-105',
            themeVisuals.gradient
          )}
        >
          {/* Subtle dot matrix grid */}
          <div className="absolute inset-0 opacity-20 bg-[radial-gradient(#ffffff22_1px,transparent_1px)] [background-size:14px_14px]" />
          
          {/* Ambient luminous orb */}
          <div 
            className={cn(
              'absolute -top-8 -right-8 w-36 h-36 rounded-full blur-2xl transition-opacity duration-500 opacity-60 group-hover:opacity-85',
              themeVisuals.glowColor
            )} 
          />

          {/* Watermark Category Glyph */}
          <div className="absolute -bottom-4 -right-2 text-white/[0.06] group-hover:text-white/[0.12] transition-all duration-500 transform rotate-12 group-hover:rotate-6 group-hover:scale-110">
            <WatermarkIcon className="w-28 h-28 stroke-[1.2]" />
          </div>

          {/* Vignette bottom shadow to blend with card surface */}
          <div className="absolute inset-0 bg-gradient-to-t from-[#27150A] via-[#27150A]/20 to-black/20" />
        </div>

        {/* Signature Luma Calendar Badge (Top-Left) */}
        <div className="absolute top-3 left-3 z-10 flex flex-col items-center justify-center min-w-[48px] px-2.5 py-1.5 rounded-xl bg-black/65 backdrop-blur-md border border-white/15 shadow-lg group-hover:border-white/30 transition-colors">
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
        <div className="flex flex-col gap-2">
          {/* Subtitle row: Status + Time indicator */}
          <div className="flex items-center justify-between gap-2 text-xs">
            <StatusChip status={hackathon.status} />
            {!isClosed && (
              <span className="font-mono text-text-muted flex items-center gap-1 text-[11px]">
                <Clock className="w-3 h-3 text-text-muted/70" />
                {deadline}
              </span>
            )}
          </div>

          {/* Event Title */}
          <h3 className="font-sans font-semibold text-base sm:text-[17px] text-text-primary leading-snug line-clamp-2 min-h-[2.6rem] group-hover:text-accent transition-colors duration-200">
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
              <div className="flex items-center gap-1 min-w-0">
                <span className="text-text-muted/80">By</span>
                <span className="font-medium text-text-primary/95 truncate">
                  {hackathon.organizerName}
                </span>
                {(hackathon.prestigeTier === 'T1' || hackathon.prestigeTier === 'T2') && (
                  <CheckCircle2 className="w-3.5 h-3.5 text-accent flex-shrink-0 inline-block" />
                )}
              </div>
            </div>

            {/* Scope Flag */}
            <span 
              className="text-xs px-2 py-0.5 rounded-full bg-black/30 border border-white/10 text-text-muted flex-shrink-0"
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
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/[0.05] border border-white/10 text-xs font-mono font-medium text-text-primary">
            <Trophy className="w-3.5 h-3.5 text-amber-400" />
            <span className="truncate">{prizeDisplay}</span>
          </div>

          {/* Category tags */}
          <div className="flex items-center gap-1.5 flex-wrap justify-end">
            {cleanTags.map((tag) => (
              <span
                key={tag}
                className={cn(
                  'px-2 py-0.5 rounded-full text-[11px] font-mono border truncate max-w-[110px]',
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
