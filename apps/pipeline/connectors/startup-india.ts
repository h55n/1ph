// apps/pipeline/connectors/startup-india.ts
import axios from 'axios'
import * as cheerio from 'cheerio'
import type { IConnector, ConnectorResult, RawHackathon } from './base'

export class StartupIndiaConnector implements IConnector {
  source = 'STARTUP_INDIA'

  async fetch(): Promise<ConnectorResult> {
    const records: RawHackathon[] = []
    const errors: string[] = []

    const urls = [
      'https://www.startupindia.gov.in/content/sih/en/innov8/challenges.html',
      'https://sih.gov.in/',
    ]

    for (const url of urls) {
      try {
        const { data } = await axios.get(url, {
          headers: { 'User-Agent': 'Mozilla/5.0 (compatible; 1ph-bot/1.0)' },
          timeout: 15000,
        })

        const $ = cheerio.load(data)

        // Generic card/listing selectors — adjust to actual page structure
        $('[class*="challenge"], [class*="hackathon"], [class*="card"]').each((_, el) => {
          try {
            const title = $(el).find('h2, h3, [class*="title"]').first().text().trim()
            const link = $(el).find('a').first().attr('href') ?? ''
            const dateText = $(el).find('[class*="date"], time').first().text().trim()

            if (!title || title.length < 5) return

            const applyUrl = link.startsWith('http') ? link : `https://www.startupindia.gov.in${link}`
            const registrationClose = parseDateText(dateText) ?? new Date(Date.now() + 60 * 24 * 60 * 60 * 1000).toISOString()

            records.push({
              sourceId: `si-${Buffer.from(title).toString('base64').slice(0, 16)}`,
              title,
              organizerName: 'Startup India / DPIIT',
              applyUrl,
              registrationClose,
              mode: 'ONLINE',
              themeTags: ['Open', 'Social Impact'],
              scope: 'INDIA',
              eligibility: 'STUDENTS',
              durationType: 'CUSTOM',
              sponsors: ['DPIIT', 'Government of India'],
            })
          } catch (err) {
            errors.push(`StartupIndia parse error: ${err}`)
          }
        })
      } catch (err) {
        errors.push(`StartupIndia fetch error for ${url}: ${err}`)
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

function parseDateText(text: string): string | null {
  try {
    const d = new Date(text)
    if (!isNaN(d.getTime())) return d.toISOString()

    // Try DD/MM/YYYY or DD-MM-YYYY
    const match = text.match(/(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})/)
    if (match) {
      return new Date(`${match[3]}-${match[2].padStart(2,'0')}-${match[1].padStart(2,'0')}`).toISOString()
    }
  } catch { /* fall through */ }
  return null
}
