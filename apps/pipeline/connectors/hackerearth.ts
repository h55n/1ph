// apps/pipeline/connectors/hackerearth.ts
import axios from 'axios'
import type { IConnector, ConnectorResult, RawHackathon } from './base'

export class HackerEarthConnector implements IConnector {
  source = 'HACKEREARTH'

  async fetch(): Promise<ConnectorResult> {
    const records: RawHackathon[] = []
    const errors: string[] = []

    try {
      const { data } = await axios.get('https://www.hackerearth.com/api/v2/challenges/', {
        params: { type: 'hackathon', status: 'upcoming,ongoing', limit: 100 },
        headers: { 'User-Agent': 'Mozilla/5.0 (compatible; 1ph-bot/1.0)' },
        timeout: 15000,
      })

      const challenges = data?.results ?? []

      for (const c of challenges) {
        try {
          records.push({
            sourceId: String(c.id ?? c.slug),
            title: c.title,
            organizerName: c.account?.name ?? 'HackerEarth',
            applyUrl: c.url ?? `https://www.hackerearth.com/challenges/hackathon/${c.slug}/`,
            registrationClose: c.end_tz ?? c.end_date,
            registrationOpen: c.start_tz ?? c.start_date,
            eventStart: c.start_tz ?? c.start_date,
            description: c.description?.slice(0, 500),
            mode: 'ONLINE',
            themeTags: c.tags?.map((t: { name: string }) => t.name) ?? ['Open'],
            scope: c.country === 'IN' ? 'INDIA' : 'GLOBAL',
            eligibility: 'OPEN',
            durationType: 'CUSTOM',
          })
        } catch (err) {
          errors.push(`HackerEarth parse error: ${err}`)
        }
      }
    } catch (err) {
      errors.push(`HackerEarth fetch error: ${err}`)
      return { source: this.source, records, errors, status: 'FAILED' }
    }

    return {
      source: this.source,
      records,
      errors,
      status: errors.length > 0 && records.length === 0 ? 'FAILED'
        : errors.length > 0 ? 'PARTIAL' : 'SUCCESS',
    }
  }
}
