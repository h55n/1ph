// apps/pipeline/quality-gate/index.ts
import axios from 'axios'
import type { RawHackathon } from '../connectors/base'

const KEYWORD_BLOCKLIST = [
  'quiz', 'case study', 'debate', 'trivia', 'essay contest',
  'moot court', 'management competition', 'business competition',
  'marketing competition', 'finance competition', 'stock market',
]

const COLLEGE_KEYWORDS = [
  'college', 'university', 'student club', 'coding club',
]

export interface QualityResult {
  pass: boolean
  reason?: string
}

export async function runQualityGate(record: RawHackathon): Promise<QualityResult> {
  // 1. Required fields
  if (!record.title?.trim()) return { pass: false, reason: 'Missing title' }
  if (!record.organizerName?.trim()) return { pass: false, reason: 'Missing organizer name' }
  if (!record.applyUrl?.trim()) return { pass: false, reason: 'Missing apply URL' }
  if (!record.registrationClose) return { pass: false, reason: 'Missing registration close date' }

  // 2. Registration close must be in the future
  const closeDate = new Date(record.registrationClose)
  if (isNaN(closeDate.getTime())) return { pass: false, reason: 'Invalid registration close date' }
  if (closeDate < new Date()) return { pass: false, reason: 'Registration already closed' }

  // 3. Keyword blocklist — title + description
  const combined = `${record.title} ${record.description ?? ''}`.toLowerCase()
  for (const keyword of KEYWORD_BLOCKLIST) {
    if (combined.includes(keyword)) {
      return { pass: false, reason: `Keyword blocklist match: "${keyword}"` }
    }
  }

  // 4. College hackathon sponsor check
  const orgLower = record.organizerName.toLowerCase()
  const isCollegeOrg = COLLEGE_KEYWORDS.some(kw => orgLower.includes(kw))
  if (isCollegeOrg && (!record.sponsors || record.sponsors.length === 0)) {
    return { pass: false, reason: 'College hackathon without named sponsor' }
  }

  // 5. Optional URL health check (disabled in ingestion by default)
  if (process.env.QUALITY_GATE_CHECK_URL !== 'true') {
    return { pass: true }
  }

  try {
    // Tight limits keep ingestion moving; richer URL validation belongs in periodic sweep jobs.
    const response = await axios.head(record.applyUrl, {
      timeout: 2500,
      maxRedirects: 2,
      validateStatus: s => s < 500,
    })
    if (response.status >= 400) {
      return { pass: false, reason: `Apply URL returned ${response.status}` }
    }
  } catch {
    // If URL check times out or errors, flag but still allow (don't block on network issues)
    console.warn(`URL check failed for ${record.applyUrl} — allowing with flag`)
  }

  return { pass: true }
}
