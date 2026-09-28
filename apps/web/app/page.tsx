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

function filterDemoHackathons(params: SearchParams) {
  const { scope, q, theme, mode, fee, team, eligibility, duration, sort, status, city } = params
  let filtered = [...demoHackathons]

  if (status === 'CLOSED') filtered = filtered.filter((h) => h.status === 'CLOSED')
  else filtered = filtered.filter((h) => ['OPEN', 'CLOSING_SOON', 'UPCOMING'].includes(h.status))

  if (scope && scope !== 'all') filtered = filtered.filter((h) => h.scope === scope)

  if (theme) {
    const themeMap: Record<string, string[]> = {
      "AI/ML": ["ai", "ml", "artificial intelligence", "machine learning", "deep learning", "nlp", "genai", "llm", "neural"],
      "Web3": ["web3", "crypto", "blockchain", "ethereum", "solana", "nft", "dao", "defi", "smart contract"],
      "Fintech": ["fintech", "finance", "banking", "payment", "trading"],
      "Health": ["health", "medtech", "healthcare", "medical", "fitness", "bio"],
      "Gaming": ["gaming", "game", "unity", "unreal", "godot", "vr"],
      "Social Impact": ["social impact", "sustainability", "climate", "environment", "green", "clean"],
      "EdTech": ["edtech", "education", "learning", "student", "school"],
      "Hardware": ["hardware", "iot", "robotics", "embedded", "arduino"],
      "Open": ["open", "all", "general", "beginner", "hack"],
    }
    const keywords = (themeMap[theme] || [theme]).map((k) => k.toLowerCase())
    filtered = filtered.filter((h) => {
      const inTags = h.themeTags.some((tag) => keywords.some((kw) => tag.toLowerCase().includes(kw)))
      const inTitle = keywords.some((kw) => h.title.toLowerCase().includes(kw))
      const inDesc = keywords.some((kw) => h.description.toLowerCase().includes(kw))
      return inTags || inTitle || inDesc
    })
  }

  if (mode) filtered = filtered.filter((h) => h.mode === mode)
  if (eligibility) filtered = filtered.filter((h) => h.eligibility === eligibility)
  if (duration) filtered = filtered.filter((h) => h.durationType === duration)
  if (fee === 'free') filtered = filtered.filter((h) => !h.entryFee)
  if (fee === 'paid') filtered = filtered.filter((h) => Number(h.entryFee ?? 0) > 0)
  if (team === 'solo') filtered = filtered.filter((h) => h.teamSizeMax === 1)
  if (team === '2-4') filtered = filtered.filter((h) => (h.teamSizeMin <= 4) && (h.teamSizeMax ?? 99) >= 2)
  if (team === '5+') filtered = filtered.filter((h) => (h.teamSizeMax ?? 99) >= 5)

  if (q) {
    const tokens = q.toLowerCase().trim().split(/\s+/).filter(Boolean)
    filtered = filtered.filter((h) => {
      const searchable = `${h.title} ${h.organizerName} ${h.themeTags.join(' ')} ${h.description} ${h.indiaRegion ?? ''} ${h.source}`.toLowerCase()
      return tokens.every((token) => searchable.includes(token))
    })
  }

  if (city) {
    const query = city.toLowerCase()
    const cityMap: Record<string, string[]> = {
      delhi: ["delhi", "ncr", "noida", "gurgaon", "gurugram"],
      bengaluru: ["bengaluru", "bangalore"],
      mumbai: ["mumbai", "navi mumbai", "thane"],
      pune: ["pune"],
      hyderabad: ["hyderabad", "telangana"],
      chennai: ["chennai", "tamil nadu"],
    }
    const synonyms = cityMap[query] || [query]
    filtered = filtered.filter((h) =>
      synonyms.some((s) =>
        h.indiaRegion?.toLowerCase().includes(s) ||
        h.title.toLowerCase().includes(s) ||
        h.description.toLowerCase().includes(s)
      )
    )
  }

  filtered.sort((a, b) => {
    if (sort === 'prestige') {
      const tierMap: Record<string, number> = { T1: 1, T2: 2, T3: 3 }
      const diff = (tierMap[a.prestigeTier] ?? 3) - (tierMap[b.prestigeTier] ?? 3)
      if (diff !== 0) return diff
      return (Number(b.prizePool ?? 0) - Number(a.prizePool ?? 0))
    }
    if (sort === 'deadline') {
      const timeA = a.registrationClose ? a.registrationClose.getTime() : Infinity
      const timeB = b.registrationClose ? b.registrationClose.getTime() : Infinity
      return timeA - timeB
    }
    if (sort === 'prize') {
      return (Number(b.prizePool ?? 0) - Number(a.prizePool ?? 0))
    }
    // Default: 'newest'
    return b.createdAt.getTime() - a.createdAt.getTime()
  })

  return filtered
}

function renderHackathonList(hackathons: any[], total: number, pageSize: number) {
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
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 sm:gap-6">
        {hackathons.map((h, i) => (
          <HackathonCard
            key={h.id}
            hackathon={{
              ...h,
              prizePool: h.prizePool ? Number(h.prizePool) : null,
              entryFee: h.entryFee ? Number(h.entryFee) : null,
              registrationClose: h.registrationClose ? new Date(h.registrationClose) : null,
            }}
            index={i}
          />
        ))}
      </div>
      <Pagination totalItems={total} pageSize={pageSize} />
    </>
  )
}

async function HackathonGrid({ searchParams }: { searchParams: Promise<SearchParams> }) {
  const resolvedParams = await searchParams
  const { scope, q, theme, mode, fee, team, eligibility, duration, sort, status, city, page } = resolvedParams
  const PAGE_SIZE = 16
  const parsedPage = parseInt(page ?? '1', 10)
  const pageNum = isNaN(parsedPage) ? 1 : Math.max(1, parsedPage)

  if (shouldUseDemoData()) {
    const filtered = filterDemoHackathons(resolvedParams)
    const total = filtered.length
    const finalHackathons = filtered.slice((pageNum - 1) * PAGE_SIZE, pageNum * PAGE_SIZE)
    return renderHackathonList(finalHackathons, total, PAGE_SIZE)
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
  if (team === '5+') andArr.push({ teamSizeMax: { gte: 5 } })

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
    newest:   { createdAt: 'desc' },
    prestige: [
      { prestigeTier: 'asc' },
      { registrationClose: 'asc' }
    ],
    deadline: { registrationClose: 'asc' },
    prize:    { prizePool: 'desc' },
  }
  
  const orderBy = SORT_MAP[sort ?? 'newest'] ?? SORT_MAP.newest

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
    console.error('Database connection unavailable, seamlessly falling back to cached directory:', hackathonsSettled.reason)
    const filtered = filterDemoHackathons(resolvedParams)
    const fallbackTotal = filtered.length
    const fallbackPage = filtered.slice((pageNum - 1) * PAGE_SIZE, pageNum * PAGE_SIZE)
    return renderHackathonList(fallbackPage, fallbackTotal, PAGE_SIZE)
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
    const hasSearchOrFilters = Boolean(q || theme || mode || fee || city || team || eligibility || duration || (scope && scope !== 'all'))
    if (!hasSearchOrFilters) {
      const filtered = filterDemoHackathons(resolvedParams)
      return renderHackathonList(filtered.slice((pageNum - 1) * PAGE_SIZE, pageNum * PAGE_SIZE), filtered.length, PAGE_SIZE)
    }

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
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 sm:gap-6">
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
