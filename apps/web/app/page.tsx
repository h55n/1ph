import { Suspense } from 'react'
import { prisma } from '@/lib/db'
import { HackathonCard } from '@/components/HackathonCard'
import { SkeletonGrid } from '@/components/SkeletonCard'
import { ScopeToggle } from '@/components/ScopeToggle'
import { FilterBar } from '@/components/FilterBar'
import { SearchBar } from '@/components/SearchBar'
import type { Prisma } from '@prisma/client'

export const revalidate = 1800

interface SearchParams {
  scope?: string
  q?: string
  theme?: string
  mode?: string
  fee?: string
  team?: string
  eligibility?: string
  duration?: string
  sort?: string
  status?: string
  city?: string
}

async function HackathonGrid({ searchParams }: { searchParams: Promise<SearchParams> }) {
  const { scope, q, theme, mode, fee, team, eligibility, duration, sort, status, city } = await searchParams

  const where: Prisma.HackathonWhereInput = {}

  if (status === 'CLOSED') {
    where.status = 'CLOSED'
  } else {
    where.status = { in: ['OPEN', 'CLOSING_SOON', 'UPCOMING'] }
  }

  if (scope && scope !== 'all') where.scope = scope as 'GLOBAL' | 'INDIA'
  if (theme) where.themeTags = { has: theme }
  if (mode) where.mode = mode as 'ONLINE' | 'OFFLINE' | 'HYBRID'
  if (eligibility) where.eligibility = eligibility as 'STUDENTS' | 'OPEN' | 'PROFESSIONALS'
  if (duration) where.durationType = duration as 'HR24' | 'HR48' | 'WEEK' | 'MONTH' | 'CUSTOM'
  if (fee === 'free') where.entryFee = null
  if (fee === 'paid') where.entryFee = { not: null }
  if (team === 'solo') where.teamSizeMax = 1
  if (team === '2-4') where.AND = [{ teamSizeMin: { lte: 4 } }, { teamSizeMax: { gte: 2 } }]

  if (q) {
    where.OR = [
      { title: { contains: q, mode: 'insensitive' as const } },
      { organizerName: { contains: q, mode: 'insensitive' as const } },
      { themeTags: { has: q } },
    ]
  }

  if (city) {
    const ci = city.toLowerCase()
    const cityOr: Prisma.HackathonWhereInput[] = [
      { indiaRegion: { contains: ci, mode: 'insensitive' as const } },
      { title: { contains: ci, mode: 'insensitive' as const } },
      { description: { contains: ci, mode: 'insensitive' as const } },
    ]
    if (where.AND) {
      if (Array.isArray(where.AND)) {
        where.AND.push({ OR: cityOr })
      } else {
        where.AND = [where.AND, { OR: cityOr }]
      }
    } else {
      where.AND = [{ OR: cityOr }]
    }
  }

  const SORT_MAP: Record<string, Prisma.HackathonOrderByWithRelationInput> = {
    prestige: { prestigeTier: 'asc' },
    deadline: { registrationClose: 'asc' },
    prize:    { prizePool: 'desc' },
    newest:   { createdAt: 'desc' },
  }
  const orderBy = SORT_MAP[sort ?? 'prestige'] ?? SORT_MAP.prestige

  const [hackathonsSettled, totalSettled] = await Promise.allSettled([
    prisma.hackathon.findMany({
      where,
      orderBy,
      take: 60,
      select: {
        slug: true, title: true, organizerName: true, organizerLogoUrl: true,
        prestigeTier: true, status: true, prizePool: true, prizeCurrency: true,
        prizeDescription: true, entryFee: true, entryFeeCurrency: true,
        registrationClose: true, mode: true, themeTags: true, scope: true,
        description: true,
      },
    }),
    prisma.hackathon.count({ where }),
  ])

  const hackathons = hackathonsSettled.status === 'fulfilled' ? hackathonsSettled.value : []
  const total = totalSettled.status === 'fulfilled' ? totalSettled.value : 0

  if (hackathonsSettled.status === 'rejected') {
    console.error('Failed to query hackathons:', hackathonsSettled.reason)
  }

  if (hackathons.length === 0) {
    return (
      <div className="text-center py-20">
        <p className="font-serif text-2xl text-text-muted mb-2">No hackathons found.</p>
        <p className="text-sm font-mono text-text-muted">Try adjusting your filters.</p>
      </div>
    )
  }

  return (
    <>
      <p className="text-sm font-mono text-text-muted mb-4">
        {total} hackathon{total !== 1 ? 's' : ''} found
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {hackathons.map((h, i) => (
          <HackathonCard
            key={h.slug}
            hackathon={{
              ...h,
              prizePool: h.prizePool ? Number(h.prizePool) : null,
              entryFee: h.entryFee ? Number(h.entryFee) : null,
              registrationClose: h.registrationClose,
            }}
            index={i}
          />
        ))}
      </div>
    </>
  )
}

export default async function HomePage({ searchParams }: { searchParams: Promise<SearchParams> }) {
  const { status } = await searchParams
  const isClosedView = status === 'CLOSED'

  return (
    <div className="space-y-6">
      <div className="pt-4 pb-2">
        <h1 className="font-serif text-4xl md:text-5xl text-text-primary mb-2">
          Every hackathon.{' '}
          <span className="text-accent">One place.</span>
        </h1>
        <p className="text-text-muted font-mono text-sm">
          No ads. No noise. Just hackathons worth your time.
        </p>
      </div>

      <div className="space-y-3">
        <div className="flex items-center gap-3 flex-wrap">
          <ScopeToggle />
          <SearchBar />
        </div>

        <div className="flex items-center gap-2">
          <a
            href="/"
            className={`px-3 py-1 rounded-chip text-xs font-mono border transition-all duration-150 ${
              !isClosedView
                ? 'border-accent text-accent bg-accent/10'
                : 'border-border text-text-muted hover:text-text-primary'
            }`}
          >
            Open
          </a>
          <a
            href="/?status=CLOSED"
            className={`px-3 py-1 rounded-chip text-xs font-mono border transition-all duration-150 ${
              isClosedView
                ? 'border-border text-text-muted bg-tag-bg'
                : 'border-border text-text-muted hover:text-text-primary'
            }`}
          >
            Closed
          </a>
        </div>

        <FilterBar />
      </div>

      <Suspense fallback={<SkeletonGrid />}>
        <HackathonGrid searchParams={searchParams} />
      </Suspense>
    </div>
  )
}
