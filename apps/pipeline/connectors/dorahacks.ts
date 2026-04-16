// apps/pipeline/connectors/dorahacks.ts
import axios from 'axios'
import type { IConnector, ConnectorResult, RawHackathon } from './base'

export class DoraHacksConnector implements IConnector {
  source = 'DORAHACKS'

  async fetch(): Promise<ConnectorResult> {
    const records: RawHackathon[] = []
    const errors: string[] = []

    try {
      const { data } = await axios.get('https://dorahacks.io/api/hackathon/list', {
        params: { limit: 50, status: 'open,upcoming' },
        headers: {
          'User-Agent': 'Mozilla/5.0 (compatible; 1ph-bot/1.0)',
          Accept: 'application/json',
        },
        timeout: 15000,
      })

      const hackathons = data?.data?.hackathons ?? data?.hackathons ?? []

      for (const h of hackathons) {
        try {
          const prizeRaw = h.total_prize ?? h.prize_pool ?? 0
          records.push({
            sourceId: String(h.id ?? h._id),
            title: h.title ?? h.name,
            organizerName: h.organization?.name ?? h.org_name ?? 'DoraHacks',
            applyUrl: `https://dorahacks.io/hackathon/${h.id ?? h.slug}`,
            registrationClose: h.registration_end ?? h.end_time,
            registrationOpen: h.registration_start ?? h.start_time,
            eventStart: h.start_time,
            eventEnd: h.end_time,
            description: h.description?.slice(0, 500),
            mode: 'ONLINE',
            prizePool: typeof prizeRaw === 'number' ? prizeRaw : parseFloat(prizeRaw) || undefined,
            prizeCurrency: 'USD',
            themeTags: h.tags ?? ['Open'],
            scope: 'GLOBAL',
            eligibility: 'OPEN',
            durationType: 'CUSTOM',
            organizerLogoUrl: h.organization?.logo ?? undefined,
          })
        } catch (err) {
          errors.push(`DoraHacks parse error for ${h.id}: ${err}`)
        }
      }
    } catch (err) {
      errors.push(`DoraHacks fetch error: ${err}`)
      return { source: this.source, records, errors, status: 'FAILED' }
    }

    return {
      source: this.source,
      records,
      errors,
      status: errors.length > 0 && records.length === 0 ? 'FAILED' : errors.length > 0 ? 'PARTIAL' : 'SUCCESS',
    }
  }
}
