// apps/pipeline/connectors/hackerrank.ts
// Uses Puppeteer — HackerRank is JS-rendered
// Filters to hackathon/build type contests only

import type { IConnector, ConnectorResult, RawHackathon } from './base'

const HACKATHON_KEYWORDS_PATTERN = /(hack|build|code|coding|contest|challenge|sprint|codesprint|codestorm)/

export class HackerRankConnector implements IConnector {
  source = 'HACKERRANK'

  async fetch(): Promise<ConnectorResult> {
    const records: RawHackathon[] = []
    const errors: string[] = []

    try {
      // Dynamic import to avoid loading puppeteer unless needed
      const puppeteer = await import('puppeteer')
      const browser = await puppeteer.default.launch({
        executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || undefined,
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
      })

      const page = await browser.newPage()
      await page.setUserAgent(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0 Safari/537.36'
      )

      await page.goto('https://www.hackerrank.com/contests?filter=hackathon', {
        waitUntil: 'networkidle2',
        timeout: 30000,
      })

      // Wait for contest cards
      await page.waitForSelector('.contest-tile, [data-contest]', { timeout: 10000 })
        .catch(() => null) // Don't crash if selector not found

      const data = await page.evaluate(() => {
        const cards = document.querySelectorAll('.contest-tile, [data-contest], [class*="contest-card"]')
        return Array.from(cards).map((card: Element) => ({
          title: card.querySelector('h2, h3, [class*="title"]')?.textContent?.trim() ?? '',
          link: (card.querySelector('a') as HTMLAnchorElement)?.href ?? '',
          dateText: card.querySelector('[class*="date"], time')?.textContent?.trim() ?? '',
          description: card.querySelector('p, [class*="description"]')?.textContent?.trim() ?? '',
        }))
      })

      await browser.close()

      for (const item of data) {
        if (!item.title || !item.link) continue
        const text = `${item.title} ${item.description ?? ''}`.toLowerCase()
        if (!HACKATHON_KEYWORDS_PATTERN.test(text)) continue

        records.push({
          sourceId: `hr-${item.link.split('/').filter(Boolean).pop() ?? Buffer.from(item.title).toString('base64').slice(0,12)}`,
          title: item.title,
          organizerName: 'HackerRank',
          applyUrl: item.link,
          registrationClose: parseDate(item.dateText) ?? new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
          mode: 'ONLINE',
          description: item.description.slice(0, 500),
          themeTags: ['Open'],
          scope: 'GLOBAL',
          eligibility: 'OPEN',
          durationType: 'CUSTOM',
        })
      }
    } catch (err) {
      errors.push(`HackerRank error: ${err}`)
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

function parseDate(text: string): string | null {
  if (!text) return null
  try {
    const d = new Date(text)
    if (!isNaN(d.getTime()) && d > new Date()) return d.toISOString()
  } catch { /* fall through */ }
  return null
}
