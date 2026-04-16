// apps/pipeline/tier-engine/index.ts
import { T1_ORGS, isIITNationalHackathon } from './t1-orgs'

interface TierInput {
  organizerName: string
  title: string
  prizePool?: number
  prizeCurrency?: string
  sponsors?: string[]
  isVerified?: boolean
  source?: string
}

function toUSD(amount: number, currency?: string): number {
  if (!currency || currency.toUpperCase() === 'USD') return amount
  if (currency.toUpperCase() === 'INR') return amount / 83  // approximate
  return amount
}

export function assignTier(input: TierInput): 'T1' | 'T2' | 'T3' {
  const orgLower = input.organizerName.toLowerCase()
  const prizeUSD = input.prizePool ? toUSD(input.prizePool, input.prizeCurrency) : 0

  // ── TIER 1 ──────────────────────────────────────────────
  const isT1Org = T1_ORGS.some(org => orgLower.includes(org))
  const isT1Prize = prizeUSD >= 50000
  const isT1IIT = isIITNationalHackathon(input.title, input.organizerName)
  const isT1MLH = input.source === 'MLH'

  if (isT1Org || isT1Prize || isT1IIT || isT1MLH) return 'T1'

  // ── TIER 2 ──────────────────────────────────────────────
  const isT2Prize = prizeUSD >= 5000
  const isT2Sponsored = input.isVerified && (input.sponsors?.length ?? 0) > 0
  const isT2Source = ['DEVPOST', 'DEVFOLIO', 'DORAHACKS'].includes(input.source ?? '')

  if (isT2Prize || isT2Sponsored || isT2Source) return 'T2'

  // ── TIER 3 ──────────────────────────────────────────────
  return 'T3'
}
