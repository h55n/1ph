// apps/pipeline/connectors/unstop.ts
// Unstop Puppeteer scraper — India-focused
// URL: https://unstop.com/hackathons
// CRITICAL: Filter to hackathons/build-a-thons ONLY — skip case studies, quizzes, debates
// 3s random delay between pages — high block risk (R1)
// Return PARTIAL on any block — never crash the pipeline

import puppeteer, { Browser } from 'puppeteer'
import type { IConnector, ConnectorResult, RawHackathon } from './base'

const KEYWORD_BLOCKLIST = [
  'quiz', 'case study', 'case-study', 'debate', 'trivia', 'essay',
  'management competition', 'moot court', 'business plan', 'quiz bowl',
]

const USER_AGENTS = [
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
]

function randomUA(): string {
  return USER_AGENTS[Math.floor(Math.random() * USER_AGENTS.length)]
}

function randomDelay(): Promise<void> {
  // 3–4s random delay per page load
  return new Promise(r => setTimeout(r, 3000 + Math.random() * 1000))
}

function isBlocklisted(title: string, description: string): boolean {
  const text = `${title} ${description}`.toLowerCase()
  return KEYWORD_BLOCKLIST.some(kw => text.includes(kw))
}

interface ScrapedOpportunity {
  id?: string
  title: string
  organizer: string
  url: string
  deadline?: string
  startDate?: string
  prize?: string
  city?: string
  isOnline?: boolean
  tags: string[]
  description?: string
  teamMin?: number
  teamMax?: number
  logo?: string
}

export class UnstopConnector implements IConnector {
  source = 'UNSTOP'

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
          '--disable-blink-features=AutomationControlled',
        ],
      })

      const page = await browser.newPage()
      await page.setUserAgent(randomUA())
      await page.setViewport({ width: 1280, height: 800 })

      // Mask automation signals
      await page.evaluateOnNewDocument(() => {
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined })
      })

      // Block heavy resources
      await page.setRequestInterception(true)
      page.on('request', req => {
        if (['image', 'font', 'media', 'stylesheet'].includes(req.resourceType())) {
          req.abort()
        } else {
          req.continue()
        }
      })

      // Navigate to hackathons filter
      const baseUrl = 'https://unstop.com/hackathons?oppType=hackathon'

      let pageNum = 1
      const maxPages = 8

      while (pageNum <= maxPages) {
        const url = pageNum === 1 ? baseUrl : `${baseUrl}&page=${pageNum}`

        try {
          await page.goto(url, { waitUntil: 'networkidle2', timeout: 40000 })

          // Wait for opportunity cards
          const cardSelector = '.opportunity-card, un-opportunities-card, .single-card, [class*="card-wrapper"]'
          await page.waitForSelector(cardSelector, { timeout: 15000 }).catch(() => null)

          // Extra wait for dynamic content
          await new Promise(r => setTimeout(r, 2000))

          const scraped = await page.evaluate(() => {
            // Try multiple selectors since Unstop changes DOM frequently
            const cards = document.querySelectorAll(
              '.opportunity-card, .single-card, [data-ng-repeat*="opportunity"], .ng-scope.card'
            )

            const results: ScrapedOpportunity[] = []

            cards.forEach((card: Element) => {
              const titleEl = card.querySelector('h3, h2, .title, [class*="title"]')
              const orgEl = card.querySelector('.company-name, .org-name, [class*="company"], [class*="organizer"]')
              const linkEl = card.querySelector('a[href*="/p/"]') as HTMLAnchorElement | null
              const deadlineEl = card.querySelector('time, .deadline, [class*="date"], [class*="deadline"]')
              const prizeEl = card.querySelector('.prize, [class*="prize"], .winning-amount')
              const tagsEls = card.querySelectorAll('.tag, [class*="tag"], .category')
              const logoEl = card.querySelector('img') as HTMLImageElement | null
              const cityEl = card.querySelector('.city, [class*="location"], [class*="city"]')

              if (!titleEl) return

              const url = linkEl?.href ?? ''
              if (!url || !url.includes('unstop.com')) return

              results.push({
                title: titleEl.textContent?.trim() ?? '',
                organizer: orgEl?.textContent?.trim() ?? '',
                url,
                deadline: deadlineEl?.getAttribute('datetime') ?? deadlineEl?.textContent?.trim(),
                prize: prizeEl?.textContent?.trim(),
                city: cityEl?.textContent?.trim(),
                tags: Array.from(tagsEls).map((el: Element) => el.textContent?.trim() ?? '').filter(Boolean),
                logo: logoEl?.src,
                isOnline: !cityEl?.textContent?.trim(),
              })
            })
            return results
          }) as ScrapedOpportunity[]

          if (scraped.length === 0) {
            errors.push(`Unstop page ${pageNum}: no cards found (possible block or page structure change)`)
            break
          }

          for (const h of scraped) {
            // Skip blocklisted events
            if (isBlocklisted(h.title, h.description ?? '')) {
              continue
            }

            const record = this.normalize(h)
            if (record) records.push(record)
          }

          pageNum++
          await randomDelay()

        } catch (pageErr) {
          errors.push(`Unstop page ${pageNum} error: ${pageErr}`)
          // Don't crash — return what we have as PARTIAL
          break
        }
      }

    } catch (err) {
      errors.push(`Unstop browser launch error: ${err}`)
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
      status: records.length === 0 ? 'FAILED' : errors.length === 0 ? 'SUCCESS' : 'PARTIAL',
    }
  }

  private normalize(h: ScrapedOpportunity): RawHackathon | null {
    if (!h.title || !h.url) return null

    // Extract sourceId from URL: /p/some-hackathon-123 → 123 or slug
    const idMatch = h.url.match(/\/p\/([^/?#]+)-(\d+)$/) ?? h.url.match(/\/p\/([^/?#]+)/)
    const sourceId = idMatch?.[2] ?? idMatch?.[1] ?? h.url.split('/p/')[1] ?? h.url

    // Parse deadline
    let registrationClose: string
    try {
      if (h.deadline) {
        // Handle formats like "Apr 30, 2025" or ISO
        registrationClose = new Date(h.deadline).toISOString()
        if (isNaN(new Date(registrationClose).getTime())) return null
      } else {
        return null // No deadline = quality gate will reject anyway
      }
    } catch {
      return null
    }

    // Parse prize
    let prizePool: number | undefined
    if (h.prize) {
      const cleaned = h.prize.replace(/[^0-9.]/g, '')
      const parsed = parseFloat(cleaned)
      if (!isNaN(parsed) && parsed > 0) prizePool = parsed
    }

    let mode: 'ONLINE' | 'OFFLINE' | 'HYBRID' = 'ONLINE'
    if (h.city && !h.isOnline) mode = 'OFFLINE'

    return {
      sourceId,
      title: h.title,
      organizerName: h.organizer || 'Unstop Hackathon',
      organizerLogoUrl: h.logo,
      applyUrl: h.url,
      registrationClose,
      mode,
      prizePool,
      prizeCurrency: 'INR',
      prizeDescription: h.prize,
      themeTags: h.tags.slice(0, 8),
      scope: 'INDIA',
      indiaRegion: h.city ?? 'Pan-India',
      eligibility: 'OPEN',
      durationType: 'CUSTOM',
      teamSizeMin: h.teamMin ?? 1,
      teamSizeMax: h.teamMax,
      sponsors: [],
    }
  }
}
