// apps/pipeline/normalizer/index.ts
import type { RawHackathon } from '../connectors/base'
import { generateSlug } from './slug'

// Lightweight heuristic for connectors that omit explicit scope:
// country signals + India-first platforms + common Indian institution markers.
const INDIA_SCOPE_KEYWORDS_REGEX = /(india|indian|iit|nit|iiit|unstop\.com|hack2skill|devfolio)/

export interface NormalizedHackathon {
  title: string
  slug: string
  organizerName: string
  organizerLogoUrl?: string
  description: string
  longDescription?: string
  themeTags: string[]
  mode: 'ONLINE' | 'OFFLINE' | 'HYBRID'
  entryFee?: number
  entryFeeCurrency?: string
  teamSizeMin: number
  teamSizeMax?: number
  eligibility: 'STUDENTS' | 'OPEN' | 'PROFESSIONALS'
  durationType: 'HR24' | 'HR48' | 'WEEK' | 'MONTH' | 'CUSTOM'
  prizePool?: number
  prizeCurrency?: string
  prizeDescription?: string
  registrationOpen?: Date
  registrationClose: Date
  eventStart: Date
  eventEnd?: Date
  applyUrl: string
  source: string
  sourceId: string
  scope: 'GLOBAL' | 'INDIA'
  indiaRegion?: string
  sponsors: string[]
}

function inferScope(raw: RawHackathon): 'GLOBAL' | 'INDIA' {
  // If connectors provide scope explicitly, trust it.
  // Otherwise infer from India-region metadata and common India-focused text markers.
  if (raw.scope) return raw.scope
  if (raw.indiaRegion?.trim()) return 'INDIA'

  const indiaSignals = [
    raw.organizerName,
    raw.title,
    raw.description,
    raw.longDescription,
    raw.applyUrl,
  ]
    .filter(Boolean)
    .join(' ')
    .toLowerCase()

  return INDIA_SCOPE_KEYWORDS_REGEX.test(indiaSignals)
    ? 'INDIA'
    : 'GLOBAL'
}

export function normalize(raw: RawHackathon, source: string): NormalizedHackathon | null {
  try {
    const registrationClose = new Date(raw.registrationClose)
    if (isNaN(registrationClose.getTime())) return null

    const eventStart = raw.eventStart ? new Date(raw.eventStart) : registrationClose
    const description = (raw.description ?? `${raw.title} — a hackathon by ${raw.organizerName}.`).slice(0, 500)

    return {
      title: raw.title.trim(),
      slug: generateSlug(raw.title, raw.sourceId),
      organizerName: raw.organizerName.trim(),
      organizerLogoUrl: raw.organizerLogoUrl,
      description,
      longDescription: raw.longDescription,
      themeTags: raw.themeTags ?? ['Open'],
      mode: raw.mode ?? 'ONLINE',
      entryFee: raw.entryFee,
      entryFeeCurrency: raw.entryFeeCurrency ?? 'USD',
      teamSizeMin: raw.teamSizeMin ?? 1,
      teamSizeMax: raw.teamSizeMax,
      eligibility: raw.eligibility ?? 'OPEN',
      durationType: raw.durationType ?? 'CUSTOM',
      prizePool: raw.prizePool,
      prizeCurrency: raw.prizeCurrency ?? 'USD',
      prizeDescription: raw.prizeDescription,
      registrationOpen: raw.registrationOpen ? new Date(raw.registrationOpen) : undefined,
      registrationClose,
      eventStart,
      eventEnd: raw.eventEnd ? new Date(raw.eventEnd) : undefined,
      applyUrl: raw.applyUrl,
      source,
      sourceId: raw.sourceId,
      scope: inferScope(raw),
      indiaRegion: raw.indiaRegion,
      sponsors: raw.sponsors ?? [],
    }
  } catch {
    return null
  }
}
