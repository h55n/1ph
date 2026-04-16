import { Suspense } from 'react'
import { prisma } from '@/lib/db'
import { HackathonCard } from '@/components/HackathonCard'
import { SkeletonGrid } from '@/components/SkeletonCard'
import { ScopeToggle } from '@/components/ScopeToggle'
import { FilterBar } from '@/components/FilterBar'
import { SearchBar } from '@/components/SearchBar'
import type { Prisma } from '@prisma/client'

export const revalidate = 3600 // ISR: revalidate every hour

interface PageProps {
  searchParams: Promise<{
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
  }>
}

async function HackathonGrid({ searchParams }: { searchParams: Promise<any> }) {
  const { scope, q, theme, mode, fee, team, eligibility, duration, sort, status } = await searchParams

  // Build Prisma where clause
  const where: Prisma.HackathonWhereInput = {}

  // Default to showing open hackathons; allow viewing closed via ?status=CLOSED
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
      { title: { contains: q, mode: 'insensitive' } },
      { organizerName: { contains: q, mode: 'insensitive' } },
      { themeTags: { has: q } },
    ]
  }

  // Build orderBy
  const SORT_MAP: Record<string, Prisma.HackathonOrderByWithRelationInput> = {
    prestige: { prestigeTier: 'asc' },   // T1 < T2 < T3 alphabetically
    deadline: { registrationClose: 'asc' },
    prize:    { prizePool: 'desc' },
    newest:   { createdAt: 'desc' },
  }
  const orderBy = SORT_MAP[sort ?? 'prestige'] ?? SORT_MAP.prestige

  const [hackathonsResult, totalResult] = await Promise.allSettled([
    prisma.hackathon.findMany({
      where,
      orderBy,
      take: 60,
      select: {
        slug: true, title: true, organizerName: true, organizerLogoUrl: true,
        prestigeTier: true, status: true, prizePool: true, prizeCurrency: true,
        prizeDescription: true, entryFee: true, entryFeeCurrency: true,
        registrationClose: true, mode: true, themeTags: true, scope: true,
      },
    }),
    prisma.hackathon.count({ where }),
  ])

  const hackathons = hackathonsResult.status === 'fulfilled' ? hackathonsResult.value : []
  const total = totalResult.status === 'fulfilled' ? totalResult.value : 0

  if (hackathonsResult.status === 'rejected') {
    console.error('Failed to query hackathons for homepage:', hackathonsResult.reason)
  }
  if (totalResult.status === 'rejected') {
    console.error('Failed to query total hackathon count for homepage:', totalResult.reason)
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

export default async function HomePage({ searchParams }: PageProps) {
  const { status } = await searchParams
  const isClosedView = status === 'CLOSED'

  return (
    <div className="space-y-6">
      {/* Hero */}
      <div className="pt-4 pb-2">
        <h1 className="font-serif text-4xl md:text-5xl text-text-primary mb-2">
          Every hackathon.{' '}
          <span className="text-accent">One place.</span>
        </h1>
        <p className="text-text-muted font-mono text-sm">
          No ads. No noise. Just hackathons worth your time.
        </p>
      </div>

      {/* Controls */}
      <div className="space-y-3">
        <div className="flex items-center gap-3 flex-wrap">
          <ScopeToggle />
          <SearchBar />
        </div>

        {/* Status tabs */}
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

      {/* Grid */}
      <Suspense fallback={<SkeletonGrid />}>
        <HackathonGrid searchParams={searchParams} />
      </Suspense>
    </div>
  )
}
