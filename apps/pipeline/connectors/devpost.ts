// apps/pipeline/connectors/devpost.ts
// Devpost Puppeteer scraper — JS-rendered, paginated
// URL: https://devpost.com/hackathons?sort_by=Upcoming&challenge_type[]=online
// ⚠️ High block risk — 2s delay between pages, random UA rotation
// On block/error: return PARTIAL (not FAILED) to preserve already-scraped records

import puppeteer, { Browser } from 'puppeteer'
import type { IConnector, ConnectorResult, RawHackathon } from './base'

const USER_AGENTS = [
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:124.0) Gecko/20100101 Firefox/124.0',
]

function randomUA(): string {
  return USER_AGENTS[Math.floor(Math.random() * USER_AGENTS.length)]
}

function delay(ms: number): Promise<void> {
  return new Promise(r => setTimeout(r, ms))
}

interface ScrapedHack {
  title: string
  organizer: string
  url: string
  deadline?: string
  prize?: string
  submittedCount?: number
  tags: string[]
  online?: boolean
  thumbnail?: string
}

export class DevpostConnector implements IConnector {
  source = 'DEVPOST'

  async fetch(): Promise<ConnectorResult> {
    const records: RawHackathon[] = []
    const errors: string[] = []
    let browser: Browser | null = null

    try {
      browser = await puppeteer.launch({
        headless: true,
        args: [
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--disable-dev-shm-usage',
          '--disable-gpu',
          '--no-first-run',
        ],
      })

      const page = await browser.newPage()
      await page.setUserAgent(randomUA())
      await page.setViewport({ width: 1280, height: 800 })

      // Block images/fonts/media to speed up scraping
      await page.setRequestInterception(true)
      page.on('request', req => {
        if (['image', 'font', 'media'].includes(req.resourceType())) {
          req.abort()
        } else {
          req.continue()
        }
      })

      let pageNum = 1
      const maxPages = 10 // 24 per page × 10 = 240 hackathons max

      while (pageNum <= maxPages) {
        const url = `https://devpost.com/hackathons?sort_by=Upcoming&challenge_type[]=online&page=${pageNum}`

        try {
          await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 })
          await page.waitForSelector('.hackathon-tile', { timeout: 10000 }).catch(() => null)

          const scraped = await page.evaluate(() => {
            const tiles = document.querySelectorAll('.hackathon-tile')
            const results: ScrapedHack[] = []

            tiles.forEach((tile: Element) => {
              const titleEl = tile.querySelector('h3') ?? tile.querySelector('.info h2')
              const linkEl = tile.querySelector('a[href*="/hackathons/"]') as HTMLAnchorElement | null
              const orgEl = tile.querySelector('.host-label, .meta .host, span.host')
              const deadlineEl = tile.querySelector('.deadline time, .submission-period time, time')
              const prizeEl = tile.querySelector('.prize, .prizes strong')
              const tagsEls = tile.querySelectorAll('.theme, .tag, .challenge-tags li')
              const thumbEl = tile.querySelector('img.challenge-logo, img') as HTMLImageElement | null

              if (!titleEl || !linkEl) return

              results.push({
                title: titleEl.textContent?.trim() ?? '',
                organizer: orgEl?.textContent?.trim() ?? '',
                url: linkEl.href,
                deadline: deadlineEl?.getAttribute('datetime') ?? deadlineEl?.textContent?.trim(),
                prize: prizeEl?.textContent?.trim(),
                tags: Array.from(tagsEls).map((el: Element) => el.textContent?.trim() ?? '').filter(Boolean),
                online: true,
                thumbnail: thumbEl?.src,
              })
            })
            return results
          }) as ScrapedHack[]

          if (scraped.length === 0) {
            // No more results
            break
          }

          for (const h of scraped) {
            const record = this.normalize(h, pageNum)
            if (record) records.push(record)
          }

          if (scraped.length < 24) break // Last page

          pageNum++
          // 2–3s random delay between pages (R1 mitigation)
          await delay(2000 + Math.random() * 1000)

        } catch (pageErr) {
          errors.push(`Devpost page ${pageNum} error: ${pageErr}`)
          break // Stop pagination on error, return what we have
        }
      }

    } catch (err) {
      errors.push(`Devpost browser error: ${err}`)
      if (records.length === 0) {
        return { source: this.source, records: [], errors, status: 'FAILED' }
      }
    } finally {
      if (browser) {
        await browser.close().catch(() => {})
      }
    }

    return {
      source: this.source,
      records,
      errors,
      // Return PARTIAL not FAILED if we got some records — R1 mitigation
      status: records.length === 0 ? 'FAILED' : errors.length === 0 ? 'SUCCESS' : 'PARTIAL',
    }
  }

  private normalize(h: ScrapedHack, _pageNum: number): RawHackathon | null {
    if (!h.title || !h.url) return null

    // Extract sourceId from URL: /hackathons/my-hackathon → my-hackathon
    const slugMatch = h.url.match(/\/hackathons\/([^/?#]+)/)
    const sourceId = slugMatch?.[1] ?? h.url

    // Parse deadline
    let registrationClose: string
    try {
      if (h.deadline) {
        registrationClose = new Date(h.deadline).toISOString()
      } else {
        // No deadline = skip
        return null
      }
    } catch {
      return null
    }

    // Parse prize pool
    let prizePool: number | undefined
    if (h.prize) {
      const prizeNum = h.prize.replace(/[^0-9.]/g, '')
      const parsed = parseFloat(prizeNum)
      if (!isNaN(parsed) && parsed > 0) prizePool = parsed
    }

    return {
      sourceId,
      title: h.title,
      organizerName: h.organizer || 'Devpost Hackathon',
      organizerLogoUrl: h.thumbnail,
      applyUrl: h.url,
      registrationClose,
      mode: 'ONLINE',
      prizePool,
      prizeCurrency: 'USD',
      prizeDescription: h.prize,
      themeTags: h.tags.slice(0, 10),
      scope: 'GLOBAL',
      eligibility: 'OPEN',
      durationType: 'CUSTOM',
      teamSizeMin: 1,
    }
  }
}
