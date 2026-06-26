const now = new Date('2026-06-26T00:00:00.000Z')

export interface DemoHackathon {
  id: string
  title: string
  slug: string
  organizerName: string
  organizerLogoUrl: string | null
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
  source: 'DEVPOST' | 'DEVFOLIO' | 'MLH' | 'UNSTOP' | 'DORAHACKS' | 'HACKEREARTH' | 'STARTUP_INDIA' | 'HACK2SKILL' | 'HACKERRANK' | 'LUMA' | 'TOPLANG' | 'MANUAL'
  sourceId: string | null
  scope: 'GLOBAL' | 'INDIA'
  indiaRegion: string | null
  prestigeTier: 'T1' | 'T2' | 'T3'
  sponsors: string[]
  status: 'UPCOMING' | 'OPEN' | 'CLOSING_SOON' | 'CLOSED'
  isVerified: boolean
  isFeatured: boolean
  urlHealthFails: number
  createdAt: Date
  updatedAt: Date
  lastSyncedAt: Date | null
}

function daysFromNow(days: number) {
  const date = new Date(now)
  date.setUTCDate(date.getUTCDate() + days)
  return date
}

export const demoHackathons: DemoHackathon[] = [
  {
    id: 'demo-ethglobal-bengaluru',
    title: 'ETHGlobal Bengaluru',
    slug: 'ethglobal-bengaluru',
    organizerName: 'ETHGlobal',
    organizerLogoUrl: null,
    description: 'A flagship Web3 hackathon for builders creating wallets, protocols, and consumer crypto applications.',
    longDescription: 'ETHGlobal Bengaluru brings together developers, designers, and founders for a high-intensity build weekend focused on practical blockchain products. Participants can work on infrastructure, consumer apps, identity, payments, and public goods.\n\nThe event is hybrid-friendly for teams with India-based members and includes mentor sessions, sponsor tracks, and demo judging from ecosystem leaders.',
    themeTags: ['Web3', 'Blockchain', 'Open Source'],
    mode: 'OFFLINE',
    entryFee: null,
    entryFeeCurrency: 'USD',
    teamSizeMin: 1,
    teamSizeMax: 4,
    eligibility: 'OPEN',
    durationType: 'HR48',
    prizePool: 100000,
    prizeCurrency: 'USD',
    prizeDescription: '$100K in sponsor prizes',
    registrationOpen: daysFromNow(-14),
    registrationClose: daysFromNow(18),
    eventStart: daysFromNow(32),
    eventEnd: daysFromNow(34),
    applyUrl: 'https://ethglobal.com/events',
    source: 'MANUAL',
    sourceId: 'demo-ethglobal-bengaluru',
    scope: 'INDIA',
    indiaRegion: 'Bengaluru',
    prestigeTier: 'T1',
    sponsors: ['Polygon', 'Base', 'Filecoin'],
    status: 'OPEN',
    isVerified: true,
    isFeatured: true,
    urlHealthFails: 0,
    createdAt: daysFromNow(-20),
    updatedAt: daysFromNow(-1),
    lastSyncedAt: daysFromNow(-1),
  },
  {
    id: 'demo-ai-buildathon',
    title: 'Global AI Agents Buildathon',
    slug: 'global-ai-agents-buildathon',
    organizerName: 'Builders Club',
    organizerLogoUrl: null,
    description: 'An online hackathon for teams building AI agents, automation tools, and applied machine learning workflows.',
    longDescription: 'The Global AI Agents Buildathon is built for engineers and product-minded teams who want to ship useful AI systems. Tracks include coding assistants, research agents, workflow automation, safety tooling, and vertical SaaS prototypes.',
    themeTags: ['AI/ML', 'Productivity', 'SaaS'],
    mode: 'ONLINE',
    entryFee: null,
    entryFeeCurrency: 'USD',
    teamSizeMin: 1,
    teamSizeMax: 5,
    eligibility: 'OPEN',
    durationType: 'WEEK',
    prizePool: 25000,
    prizeCurrency: 'USD',
    prizeDescription: null,
    registrationOpen: daysFromNow(-5),
    registrationClose: daysFromNow(9),
    eventStart: daysFromNow(12),
    eventEnd: daysFromNow(19),
    applyUrl: 'https://devpost.com/hackathons',
    source: 'DEVPOST',
    sourceId: 'demo-ai-buildathon',
    scope: 'GLOBAL',
    indiaRegion: null,
    prestigeTier: 'T2',
    sponsors: ['Open source partners'],
    status: 'CLOSING_SOON',
    isVerified: true,
    isFeatured: false,
    urlHealthFails: 0,
    createdAt: daysFromNow(-9),
    updatedAt: daysFromNow(-2),
    lastSyncedAt: daysFromNow(-2),
  },
  {
    id: 'demo-student-impact',
    title: 'Student Climate Impact Hack',
    slug: 'student-climate-impact-hack',
    organizerName: 'Campus Labs India',
    organizerLogoUrl: null,
    description: 'A student-only challenge for climate, sustainability, and civic technology projects.',
    longDescription: 'Student Climate Impact Hack helps college teams prototype practical solutions for climate resilience, waste reduction, public transport, and environmental data. Shortlisted teams receive mentor reviews and credits for cloud deployment.',
    themeTags: ['Social Impact', 'Climate', 'Hardware'],
    mode: 'HYBRID',
    entryFee: null,
    entryFeeCurrency: 'INR',
    teamSizeMin: 2,
    teamSizeMax: 4,
    eligibility: 'STUDENTS',
    durationType: 'MONTH',
    prizePool: 500000,
    prizeCurrency: 'INR',
    prizeDescription: 'INR 5L prize pool plus incubation support',
    registrationOpen: daysFromNow(-2),
    registrationClose: daysFromNow(27),
    eventStart: daysFromNow(40),
    eventEnd: daysFromNow(70),
    applyUrl: 'https://unstop.com/hackathons',
    source: 'UNSTOP',
    sourceId: 'demo-student-impact',
    scope: 'INDIA',
    indiaRegion: 'Pune',
    prestigeTier: 'T3',
    sponsors: ['Campus Labs', 'GreenTech Forum'],
    status: 'OPEN',
    isVerified: false,
    isFeatured: false,
    urlHealthFails: 0,
    createdAt: daysFromNow(-4),
    updatedAt: daysFromNow(-1),
    lastSyncedAt: daysFromNow(-1),
  },
]

export function shouldUseDemoData() {
  return !process.env.DATABASE_URL?.trim()
}

export function findDemoHackathon(slug: string) {
  const normalizedSlug = decodeURIComponent(slug).trim().toLowerCase()
  return demoHackathons.find((row) => row.slug.toLowerCase() === normalizedSlug)
}
