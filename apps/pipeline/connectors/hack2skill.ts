// apps/pipeline/connectors/hack2skill.ts
import axios from 'axios'
import * as cheerio from 'cheerio'
import type { IConnector, ConnectorResult, RawHackathon } from './base'

export class Hack2SkillConnector implements IConnector {
  source = 'HACK2SKILL'

  async fetch(): Promise<ConnectorResult> {
    const records: RawHackathon[] = []
    const errors: string[] = []

    try {
      const { data } = await axios.get('https://hack2skill.com/hack/allhackathon', {
        headers: {
          'User-Agent': 'Mozilla/5.0 (compatible; 1ph-bot/1.0)',
          Accept: 'text/html,application/xhtml+xml',
        },
        timeout: 20000,
      })

      const $ = cheerio.load(data)

      // Hack2Skill card selectors — update if site structure changes
      $('.hackathon-card, .event-card, [class*="hackathon"]').each((_, el) => {
        try {
          const title = $(el).find('[class*="title"], h2, h3').first().text().trim()
          const orgName = $(el).find('[class*="organiz"], [class*="company"]').first().text().trim()
          const link = $(el).find('a[href*="hackathon"], a[href*="event"]').first().attr('href') ?? ''
          const dateText = $(el).find('[class*="date"], [class*="deadline"]').first().text().trim()
          const prizeText = $(el).find('[class*="prize"], [class*="reward"]').first().text().trim()
          const modeText = $(el).find('[class*="mode"], [class*="location"]').first().text().trim()

          if (!title || title.length < 5) return
          if (!link) return

          const applyUrl = link.startsWith('http') ? link : `https://hack2skill.com${link}`
          const registrationClose = parseDateFromText(dateText)
            ?? new Date(Date.now() + 45 * 24 * 60 * 60 * 1000).toISOString()

          const prizePool = extractPrize(prizeText)
          const mode = modeText.toLowerCase().includes('offline') ? 'OFFLINE'
            : modeText.toLowerCase().includes('hybrid') ? 'HYBRID' : 'ONLINE'

          records.push({
            sourceId: `h2s-${link.split('/').filter(Boolean).pop() ?? Buffer.from(title).toString('base64').slice(0,12)}`,
            title,
            organizerName: orgName || 'Hack2Skill',
            applyUrl,
            registrationClose,
            mode: mode as 'ONLINE' | 'OFFLINE' | 'HYBRID',
            prizePool: prizePool ?? undefined,
            prizeCurrency: 'INR',
            themeTags: ['Open'],
            scope: 'INDIA',
            eligibility: 'OPEN',
            durationType: 'CUSTOM',
          })
        } catch (err) {
          errors.push(`Hack2Skill parse error: ${err}`)
        }
      })
    } catch (err) {
      errors.push(`Hack2Skill fetch error: ${err}`)
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

function parseDateFromText(text: string): string | null {
  if (!text) return null
  try {
    const cleaned = text.replace(/registration closes?:?\s*/i, '').trim()
    const d = new Date(cleaned)
    if (!isNaN(d.getTime()) && d > new Date()) return d.toISOString()
    const match = cleaned.match(/(\d{1,2})[\/\-\s]([A-Za-z]+|\d{1,2})[\/\-\s](\d{4})/)
    if (match) {
      const d2 = new Date(`${match[1]} ${match[2]} ${match[3]}`)
      if (!isNaN(d2.getTime())) return d2.toISOString()
    }
  } catch { /* fall through */ }
  return null
}

function extractPrize(text: string): number | null {
  if (!text) return null
  const lakhs = text.match(/₹?\s*(\d+(?:\.\d+)?)\s*L/i)
  if (lakhs) return parseFloat(lakhs[1]) * 100000
  const k = text.match(/₹?\s*(\d+(?:\.\d+)?)\s*[Kk]/)
  if (k) return parseFloat(k[1]) * 1000
  const plain = text.match(/₹\s*(\d+)/)
  if (plain) return parseInt(plain[1])
  return null
}
