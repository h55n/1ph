// apps/pipeline/connectors/toplang.ts
import axios from 'axios'
import * as cheerio from 'cheerio'
import type { IConnector, ConnectorResult, RawHackathon } from './base'

export class ToplangConnector implements IConnector {
  source = 'TOPLANG'

  async fetch(): Promise<ConnectorResult> {
    const records: RawHackathon[] = []
    const errors: string[] = []

    const urls = [
      'https://www.devdynamics.ai/hackathons',  // common India aggregator
      'https://unstop.com/hackathons',            // fallback secondary scrape
    ]

    for (const url of urls) {
      try {
        const { data } = await axios.get(url, {
          headers: { 'User-Agent': 'Mozilla/5.0 (compatible; 1ph-bot/1.0)' },
          timeout: 15000,
        })

        const $ = cheerio.load(data)

        $('[class*="hackathon"], [class*="event-card"], [class*="contest"]').each((_, el) => {
          try {
            const title = $(el).find('h2, h3, [class*="title"]').first().text().trim()
            const link  = $(el).find('a').first().attr('href') ?? ''
            const date  = $(el).find('[class*="date"], time').first().text().trim()

            if (!title || !link) return

            const applyUrl = link.startsWith('http') ? link : `${new URL(url).origin}${link}`

            records.push({
              sourceId: `tl-${Buffer.from(title + url).toString('base64').slice(0, 16)}`,
              title,
              organizerName: 'Community',
              applyUrl,
              registrationClose: parseAnyDate(date) ?? new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
              mode: 'ONLINE',
              themeTags: ['Open'],
              scope: 'INDIA',
              eligibility: 'OPEN',
              durationType: 'CUSTOM',
            })
          } catch { /* skip malformed */ }
        })

        // Only use first successful source
        if (records.length > 0) break
      } catch (err) {
        errors.push(`Toplang fetch error for ${url}: ${err}`)
      }
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

function parseAnyDate(text: string): string | null {
  if (!text) return null
  try {
    const d = new Date(text.replace(/[^\w\s,]/g, ' ').trim())
    if (!isNaN(d.getTime()) && d > new Date()) return d.toISOString()
  } catch { /* fall through */ }
  return null
}
