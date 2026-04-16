// apps/pipeline/connectors/devfolio.ts
// Devfolio GraphQL connector — India-focused hackathon platform
// Endpoint: https://api.devfolio.co/api/search/hackathons (REST, not pure GraphQL)
// No auth required for public listings

import axios from 'axios'
import type { IConnector, ConnectorResult, RawHackathon } from './base'

interface DevfolioHackathon {
  id: string
  name: string
  slug: string
  desc?: string
  long_desc?: string
  starts_at: string
  ends_at: string
  submission_deadline?: string
  prize_pool?: string
  prize_amount?: number
  city?: string
  is_online?: boolean
  is_hybrid?: boolean
  registration_closes_at?: string
  website?: string
  hackathon_setting?: string
  themes?: Array<{ id: string; name: string }>
  sponsors?: Array<{ name: string }>
  team_min?: number
  team_max?: number
  is_open?: boolean
  status?: string
  logo?: { url?: string }
  organizer?: { name?: string; logo?: { url?: string } }
}

interface DevfolioResponse {
  count: number
  results: DevfolioHackathon[]
}

const DEVFOLIO_API = 'https://api.devfolio.co/api/search/hackathons'
const PAGE_SIZE = 24

export class DevfolioConnector implements IConnector {
  source = 'DEVFOLIO'

  async fetch(): Promise<ConnectorResult> {
    const records: RawHackathon[] = []
    const errors: string[] = []
    let page = 0

    try {
      while (true) {
        const response = await axios.post<DevfolioResponse>(
          DEVFOLIO_API,
          {
            size: PAGE_SIZE,
            from: page * PAGE_SIZE,
            filters: {
              status: ['open', 'upcoming'],
            },
          },
          {
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json',
              'User-Agent': 'Mozilla/5.0 (compatible; 1ph-pipeline/1.0)',
            },
            timeout: 15000,
          }
        )

        const data = response.data
        if (!data?.results || data.results.length === 0) break

        for (const h of data.results) {
          try {
            const record = this.normalize(h)
            if (record) records.push(record)
          } catch (err) {
            errors.push(`Failed to parse hackathon ${h.id}: ${err}`)
          }
        }

        // Pagination check
        if (data.results.length < PAGE_SIZE) break
        page++

        // Safety cap — max 500 records per run
        if (page > 20) break

        // Polite delay
        await new Promise(r => setTimeout(r, 1500))
      }
    } catch (err: any) {
      const msg = err?.response?.data
        ? `HTTP ${err.response.status}: ${JSON.stringify(err.response.data)}`
        : String(err)
      errors.push(`Devfolio fetch error: ${msg}`)

      // If we got some records before the error, return PARTIAL
      if (records.length > 0) {
        return { source: this.source, records, errors, status: 'PARTIAL' }
      }
      return { source: this.source, records: [], errors, status: 'FAILED' }
    }

    return {
      source: this.source,
      records,
      errors,
      status: errors.length === 0 ? 'SUCCESS' : 'PARTIAL',
    }
  }

  private normalize(h: DevfolioHackathon): RawHackathon | null {
    if (!h.id || !h.name) return null

    const registrationClose =
      h.registration_closes_at ?? h.submission_deadline ?? h.ends_at
    if (!registrationClose) return null

    const applyUrl = h.website ?? `https://devfolio.co/hackathons/${h.slug}`

    let mode: 'ONLINE' | 'OFFLINE' | 'HYBRID' = 'ONLINE'
    if (h.is_hybrid) mode = 'HYBRID'
    else if (h.hackathon_setting === 'offline' || (!h.is_online && h.city)) mode = 'OFFLINE'

    return {
      sourceId: h.id,
      title: h.name,
      organizerName: h.organizer?.name ?? 'Devfolio Hackathon',
      organizerLogoUrl: h.organizer?.logo?.url ?? h.logo?.url,
      applyUrl,
      registrationClose: new Date(registrationClose).toISOString(),
      registrationOpen: h.starts_at ? new Date(h.starts_at).toISOString() : undefined,
      eventStart: h.starts_at ? new Date(h.starts_at).toISOString() : undefined,
      eventEnd: h.ends_at ? new Date(h.ends_at).toISOString() : undefined,
      description: (h.desc ?? '').slice(0, 500),
      longDescription: h.long_desc ?? undefined,
      mode,
      teamSizeMin: h.team_min ?? 1,
      teamSizeMax: h.team_max ?? undefined,
      prizePool: h.prize_amount ?? undefined,
      prizeCurrency: 'INR',
      prizeDescription: h.prize_pool ?? undefined,
      themeTags: (h.themes ?? []).map(t => t.name).filter(Boolean),
      sponsors: (h.sponsors ?? []).map(s => s.name).filter(Boolean),
      scope: 'INDIA',
      indiaRegion: h.city ?? 'Pan-India',
      eligibility: 'OPEN',
      durationType: 'CUSTOM',
    }
  }
}
