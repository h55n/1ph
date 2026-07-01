import { Suspense } from 'react'
import { prisma } from '@/lib/db'
import { HackathonCard } from '@/components/HackathonCard'
import { SkeletonGrid } from '@/components/SkeletonCard'
import { ScopeToggle } from '@/components/ScopeToggle'
import { FilterBar } from '@/components/FilterBar'
import { SearchBar } from '@/components/SearchBar'
import { Pagination } from '@/components/Pagination'
import { StatusToggle } from '@/components/StatusToggle'
import type { Prisma } from '@prisma/client'
import { demoHackathons, shouldUseDemoData } from '@/lib/demo-data'

export const revalidate = 0

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
  page?: string
}

async function HackathonGrid({ searchParams }: { searchParams: Promise<SearchParams> }) {
  const { scope, q, theme, mode, fee, team, eligibility, duration, sort, status, city, page } = await searchParams
  const PAGE_SIZE = 16
  const parsedPage = parseInt(page ?? '1', 10)
  const pageNum = isNaN(parsedPage) ? 1 : Math.max(1, parsedPage)

  if (shouldUseDemoData()) {
    let filtered = [...demoHackathons]

    if (status === 'CLOSED') filtered = filtered.filter((h) => h.status === 'CLOSED')
    else filtered = filtered.filter((h) => ['OPEN', 'CLOSING_SOON', 'UPCOMING'].includes(h.status))

    if (scope && scope !== 'all') filtered = filtered.filter((h) => h.scope === scope)
    if (theme) filtered = filtered.filter((h) => h.themeTags.some((tag) => tag.toLowerCase().includes(theme.toLowerCase())) || h.title.toLowerCase().includes(theme.toLowerCase()) || h.description.toLowerCase().includes(theme.toLowerCase()))
    if (mode) filtered = filtered.filter((h) => h.mode === mode)
    if (eligibility) filtered = filtered.filter((h) => h.eligibility === eligibility)
    if (duration) filtered = filtered.filter((h) => h.durationType === duration)
    if (fee === 'free') filtered = filtered.filter((h) => !h.entryFee)
    if (fee === 'paid') filtered = filtered.filter((h) => Number(h.entryFee ?? 0) > 0)
    if (team === 'solo') filtered = filtered.filter((h) => h.teamSizeMax === 1)
    if (team === '2-4') filtered = filtered.filter((h) => h.teamSizeMin <= 4 && (h.teamSizeMax ?? 99) >= 2)
    if (q) {
      const query = q.toLowerCase()
      filtered = filtered.filter((h) => h.title.toLowerCase().includes(query) || h.organizerName.toLowerCase().includes(query) || h.themeTags.some((tag) => tag.toLowerCase().includes(query)))
    }
    if (city) {
      const query = city.toLowerCase()
      filtered = filtered.filter((h) => h.indiaRegion?.toLowerCase().includes(query) || h.title.toLowerCase().includes(query) || h.description.toLowerCase().includes(query))
    }

    filtered.sort((a, b) => {
      if (sort === 'prestige') return a.prestigeTier.localeCompare(b.prestigeTier)
      if (sort === 'deadline') return (a.registrationClose?.getTime() ?? 0) - (b.registrationClose?.getTime() ?? 0)
      if (sort === 'prize') return Number(b.prizePool ?? 0) - Number(a.prizePool ?? 0)
      return b.createdAt.getTime() - a.createdAt.getTime()
    })

    const total = filtered.length
    const finalHackathons = filtered.slice((pageNum - 1) * PAGE_SIZE, pageNum * PAGE_SIZE)

    if (finalHackathons.length === 0) {
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
          {finalHackathons.map((h, i) => (
            <HackathonCard
              key={h.id}
              hackathon={{
                ...h,
                prizePool: h.prizePool ? Number(h.prizePool) : null,
                entryFee: h.entryFee ? Number(h.entryFee) : null,
              }}
              index={i}
            />
          ))}
        </div>
        <Pagination totalItems={total} pageSize={PAGE_SIZE} />
      </>
    )
  }

  const where: Prisma.HackathonWhereInput = {
    AND: []
  }

  const andArr = where.AND as Prisma.HackathonWhereInput[]

  if (status === 'CLOSED') {
    andArr.push({ status: 'CLOSED' })
  } else {
    andArr.push({ status: { in: ['OPEN', 'CLOSING_SOON', 'UPCOMING'] } })
  }

  if (scope && scope !== 'all') andArr.push({ scope: scope as 'GLOBAL' | 'INDIA' })
  
  if (theme) {
    const themeMap: Record<string, string[]> = {
      "AI/ML": ["ai", "ml", "artificial intelligence", "machine learning", "deep learning", "nlp"],
      "Web3": ["web3", "crypto", "blockchain", "ethereum", "solana", "nft", "dao"],
      "Fintech": ["fintech", "finance", "banking", "payment", "trading"],
      "Health": ["health", "medtech", "healthcare", "medical", "fitness"],
      "Gaming": ["gaming", "game", "unity", "unreal"],
      "Social Impact": ["social impact", "sustainability", "climate", "environment"],
      "EdTech": ["edtech", "education", "learning"],
      "Hardware": ["hardware", "iot", "robotics"],
      "Open": ["open", "all", "general"],
    }
    const keywords = themeMap[theme] || [theme]
    const themeConditions: Prisma.HackathonWhereInput[] = [
      { themeTags: { has: theme } },
      ...keywords.map(kw => ({ title: { contains: kw, mode: 'insensitive' as const } })),
      ...keywords.map(kw => ({ description: { contains: kw, mode: 'insensitive' as const } })),
      ...keywords.map(kw => ({ themeTags: { has: kw } }))
    ]
    andArr.push({ OR: themeConditions })
  }

  if (mode) andArr.push({ mode: mode as 'ONLINE' | 'OFFLINE' | 'HYBRID' })
  if (eligibility) andArr.push({ eligibility: eligibility as 'STUDENTS' | 'OPEN' | 'PROFESSIONALS' })
  if (duration) andArr.push({ durationType: duration as 'HR24' | 'HR48' | 'WEEK' | 'MONTH' | 'CUSTOM' })
  if (fee === 'free') andArr.push({ OR: [{ entryFee: null }, { entryFee: 0 }] })
  if (fee === 'paid') andArr.push({ entryFee: { gt: 0 } })
  if (team === 'solo') andArr.push({ teamSizeMax: 1 })
  if (team === '2-4') andArr.push({ AND: [{ teamSizeMin: { lte: 4 } }, { teamSizeMax: { gte: 2 } }] })

  if (q) {
    andArr.push({
      OR: [
        { title: { contains: q, mode: 'insensitive' as const } },
        { organizerName: { contains: q, mode: 'insensitive' as const } },
        { themeTags: { has: q } },
      ]
    })
  }

  if (city) {
    const ci = city.toLowerCase()
    const cityOr: Prisma.HackathonWhereInput[] = [
      { indiaRegion: { contains: ci, mode: 'insensitive' as const } },
      { title: { contains: ci, mode: 'insensitive' as const } },
      { description: { contains: ci, mode: 'insensitive' as const } },
    ]
    andArr.push({ OR: cityOr })
  }

  const SORT_MAP: Record<string, Prisma.HackathonOrderByWithRelationInput | Prisma.HackathonOrderByWithRelationInput[]> = {
    prestige: [
      { prestigeTier: 'asc' },
      { registrationClose: 'asc' }
    ],
    deadline: { registrationClose: 'asc' },
    prize:    { prizePool: 'desc' },
    newest:   { createdAt: 'desc' },
  }
  
  // Default to prestige so it naturally mixes T1/T2 hackathons and highlights best ones
  const orderBy = SORT_MAP[sort ?? 'prestige'] ?? SORT_MAP.prestige

  const [hackathonsSettled, totalSettled] = await Promise.allSettled([
    prisma.hackathon.findMany({
      where,
      orderBy,
      take: PAGE_SIZE,
      skip: (pageNum - 1) * PAGE_SIZE,
      select: {
        id: true, slug: true, title: true, organizerName: true, organizerLogoUrl: true,
        prestigeTier: true, status: true, prizePool: true, prizeCurrency: true,
        prizeDescription: true, entryFee: true, entryFeeCurrency: true,
        registrationClose: true, mode: true, themeTags: true, scope: true,
        description: true, source: true,
      },
    }),
    prisma.hackathon.count({ where }),
  ])

  const hackathonsRaw = hackathonsSettled.status === 'fulfilled' ? hackathonsSettled.value : []
  const total = totalSettled.status === 'fulfilled' ? totalSettled.value : 0

  if (hackathonsSettled.status === 'rejected') {
    console.error('Failed to query hackathons:', hackathonsSettled.reason)
  }

  // Interleave by source to prevent clustering (e.g., all Unstop then all Devfolio)
  const interleaved: typeof hackathonsRaw = []
  if (hackathonsRaw.length > 0) {
    const groups: Record<string, typeof hackathonsRaw> = {}
    hackathonsRaw.forEach(h => {
      if (!groups[h.source]) groups[h.source] = []
      groups[h.source].push(h)
    })
    
    const sources = Object.keys(groups)
    let maxLen = Math.max(...sources.map(s => groups[s].length))
    
    for (let i = 0; i < maxLen; i++) {
      for (const s of sources) {
        if (groups[s][i]) {
          interleaved.push(groups[s][i])
        }
      }
    }
  }

  const finalHackathons = interleaved.length > 0 ? interleaved : hackathonsRaw

  if (finalHackathons.length === 0) {
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
        {finalHackathons.map((h, i) => (
          <HackathonCard
            key={h.id}
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
      <Pagination totalItems={total} pageSize={PAGE_SIZE} />
    </>
  )
}

export default async function HomePage({ searchParams }: { searchParams: Promise<SearchParams> }) {
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

        <StatusToggle />

        <FilterBar />
      </div>

      <Suspense fallback={<SkeletonGrid />}>
        <HackathonGrid searchParams={searchParams} />
      </Suspense>
    </div>
  )
}
