import rawHackathons from '@/data/hackathons.json'

export interface DemoHackathon {
  id: string
  title: string
  slug: string
  organizerName: string
  organizerLogoUrl: string | null
  coverImageUrl?: string | null
  category?: string | null
  description: string
  longDescription: string | null
  themeTags: string[]
  mode: 'ONLINE' | 'OFFLINE' | 'HYBRID'
  entryFee: number | null
  entryFeeCurrency: string | null
  teamSizeMin: number
  teamSizeMax: number | null
  eligibility: 'STUDENTS' | 'OPEN' | 'PROFESSIONALS'
  durationType: 'HR24' | 'HR48' | 'WEEK' | 'MONTH' | 'CUSTOM'
  prizePool: number | null
  prizeCurrency: string | null
  prizeDescription: string | null
  registrationOpen: Date | null
  registrationClose: Date | null
  eventStart: Date | null
  eventEnd: Date | null
  applyUrl: string
  source: string
  sourceId: string | null
  scope: 'GLOBAL' | 'INDIA'
  indiaRegion: string | null
  prestigeTier: 'T1' | 'T2' | 'T3'
  sponsors: string[]
  status: 'OPEN' | 'CLOSING_SOON' | 'UPCOMING' | 'CLOSED'
  isVerified: boolean
  isFeatured: boolean
  urlHealthFails: number
  createdAt: Date
  updatedAt: Date
  lastSyncedAt: Date | null
}

export const demoHackathons: DemoHackathon[] = (rawHackathons as any[]).map((h) => ({
  ...h,
  coverImageUrl: h.coverImageUrl ?? null,
  category: h.category ?? null,
  mode: h.mode as 'ONLINE' | 'OFFLINE' | 'HYBRID',
  eligibility: h.eligibility as 'STUDENTS' | 'OPEN' | 'PROFESSIONALS',
  durationType: h.durationType as 'HR24' | 'HR48' | 'WEEK' | 'MONTH' | 'CUSTOM',
  prestigeTier: h.prestigeTier as 'T1' | 'T2' | 'T3',
  status: h.status as 'OPEN' | 'CLOSING_SOON' | 'UPCOMING' | 'CLOSED',
  scope: h.scope as 'GLOBAL' | 'INDIA',
  registrationOpen: h.registrationOpen ? new Date(h.registrationOpen) : null,
  registrationClose: h.registrationClose ? new Date(h.registrationClose) : null,
  eventStart: h.eventStart ? new Date(h.eventStart) : null,
  eventEnd: h.eventEnd ? new Date(h.eventEnd) : null,
  createdAt: new Date(h.createdAt),
  updatedAt: new Date(h.updatedAt),
  lastSyncedAt: h.lastSyncedAt ? new Date(h.lastSyncedAt) : null,
}))

export function shouldUseDemoData(): boolean {
  const url = process.env.DATABASE_URL?.trim()
  if (!url || url.includes('[SENSITIVE]')) return true
  return false
}

export function findDemoHackathon(slug: string): DemoHackathon | undefined {
  const normalizedSlug = decodeURIComponent(slug).trim().toLowerCase()
  return demoHackathons.find((row) => row.slug.toLowerCase() === normalizedSlug)
}
