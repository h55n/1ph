// apps/pipeline/connectors/mlh.ts
import axios from 'axios'
import * as cheerio from 'cheerio'
import type { IConnector, ConnectorResult, RawHackathon } from './base'

export class MLHConnector implements IConnector {
  source = 'MLH'

  async fetch(): Promise<ConnectorResult> {
    const records: RawHackathon[] = []
    const errors: string[] = []

    try {
      const { data } = await axios.get('https://mlh.io/seasons/2026/events', {
        headers: { 'User-Agent': 'Mozilla/5.0 (compatible; 1ph-bot/1.0)' },
        timeout: 15000,
      })

      const $ = cheerio.load(data)

      $('.event.future').each((_, el) => {
        try {
          const title = $(el).find('.event-name').text().trim()
          const applyUrl = $(el).find('a.event-link').attr('href') ?? ''
          const dateText = $(el).find('.event-date').text().trim()
          const location = $(el).find('.event-location').text().trim()
          const logo = $(el).find('.event-logo img').attr('src') ?? undefined

          if (!title || !applyUrl) return

          // Parse date range "Jan 15 – Jan 16, 2026"
          const dateMatch = dateText.match(/([A-Za-z]+ \d+)[^,]*,?\s*(\d{4})/)
          const registrationClose = dateMatch
            ? new Date(`${dateMatch[1]}, ${dateMatch[2]}`).toISOString()
            : new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString()

          records.push({
            sourceId: applyUrl.replace('https://mlh.io/events/', '').replace('/', ''),
            title,
            organizerName: 'MLH',
            applyUrl: applyUrl.startsWith('http') ? applyUrl : `https://mlh.io${applyUrl}`,
            registrationClose,
            mode: location.toLowerCase().includes('online') ? 'ONLINE' : 'HYBRID',
            themeTags: ['Open'],
            scope: 'GLOBAL',
            eligibility: 'STUDENTS',
            durationType: 'CUSTOM',
            organizerLogoUrl: logo,
          })
        } catch (err) {
          errors.push(`MLH parse error: ${err}`)
        }
      })
    } catch (err) {
      errors.push(`MLH fetch error: ${err}`)
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
