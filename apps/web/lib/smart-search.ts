export interface SmartSearchResult {
  item: any
  score: number
  matchedTokens: string[]
}

const CITY_SYNONYMS: Record<string, string[]> = {
  delhi: ['delhi', 'ncr', 'noida', 'gurgaon', 'gurugram', 'ghaziabad', 'faridabad', 'new delhi'],
  bengaluru: ['bengaluru', 'bangalore', 'karnataka'],
  mumbai: ['mumbai', 'bombay', 'navi mumbai', 'thane', 'maharashtra'],
  pune: ['pune'],
  hyderabad: ['hyderabad', 'telangana'],
  chennai: ['chennai', 'madras', 'tamil nadu'],
  sf: ['san francisco', 'sf', 'california', 'bay area', 'silicon valley'],
  toronto: ['toronto', 'ontario', 'canada'],
  waterloo: ['waterloo', 'ontario'],
}

const THEME_SYNONYMS: Record<string, string[]> = {
  ai: ['ai', 'ml', 'machine learning', 'deep learning', 'genai', 'generative ai', 'llm', 'gpt', 'neural', 'agent', 'vision', 'multimodal'],
  web3: ['web3', 'crypto', 'blockchain', 'solana', 'ethereum', 'eth', 'nft', 'dao', 'defi', 'smart contract', 'layer2', 'metis', 'aptos'],
  fintech: ['fintech', 'finance', 'banking', 'payment', 'payments', 'upi', 'trading', 'crypto payment'],
  gaming: ['game', 'gaming', 'games', 'unity', 'unreal', 'godot', 'vr', 'ar', 'xr', 'metaverse', 'spatial'],
  health: ['health', 'medtech', 'healthcare', 'medical', 'fitness', 'bio', 'biotech'],
  hardware: ['hardware', 'iot', 'robotics', 'embedded', 'sensor', 'arduino', 'raspberry pi'],
  climate: ['climate', 'sustainability', 'green', 'clean energy', 'environment', 'social impact'],
  edtech: ['edtech', 'education', 'learning', 'student', 'school', 'university'],
}

/**
 * Perform smart, multi-token fuzzy and semantic search over hackathon records.
 */
export function smartSearchHackathons<T extends {
  title: string
  organizerName: string
  description?: string | null
  themeTags: string[]
  mode?: string
  indiaRegion?: string | null
  prizePool?: number | null
  prestigeTier?: string
  slug: string
}>(items: T[], rawQuery: string): T[] {
  const query = rawQuery.trim().toLowerCase()
  if (!query) return items

  // Tokenize query
  const queryTokens = query.split(/\s+/).filter(Boolean)

  const scored: { item: T; score: number }[] = []

  for (const item of items) {
    let score = 0
    const titleLower = item.title.toLowerCase()
    const orgLower = item.organizerName.toLowerCase()
    const descLower = (item.description || '').toLowerCase()
    const regionLower = (item.indiaRegion || '').toLowerCase()
    const modeLower = (item.mode || '').toLowerCase()
    const tagsLower = item.themeTags.map((t) => t.toLowerCase())

    // 1. Exact full query matches
    if (titleLower.includes(query)) score += 120
    if (orgLower.includes(query)) score += 90
    if (descLower.includes(query)) score += 50
    if (regionLower.includes(query)) score += 60

    // 2. Token-by-token matching
    let allTokensMatched = true
    for (const token of queryTokens) {
      let tokenMatched = false

      // Title match
      if (titleLower.includes(token)) {
        score += 35
        tokenMatched = true
      }

      // Organizer match
      if (orgLower.includes(token)) {
        score += 25
        tokenMatched = true
      }

      // Tags match
      if (tagsLower.some((t) => t.includes(token))) {
        score += 30
        tokenMatched = true
      }

      // Description match
      if (descLower.includes(token)) {
        score += 15
        tokenMatched = true
      }

      // Location / Mode match
      if (regionLower.includes(token) || modeLower.includes(token)) {
        score += 20
        tokenMatched = true
      }

      // Theme synonyms check
      for (const [themeKey, syns] of Object.entries(THEME_SYNONYMS)) {
        if (syns.includes(token)) {
          // If hackathon tags or title contain any synonym
          if (tagsLower.some((t) => syns.some((s) => t.includes(s))) ||
              syns.some((s) => titleLower.includes(s) || descLower.includes(s))) {
            score += 25
            tokenMatched = true
          }
        }
      }

      // City synonyms check
      for (const [cityKey, syns] of Object.entries(CITY_SYNONYMS)) {
        if (syns.includes(token)) {
          if (syns.some((s) => regionLower.includes(s) || titleLower.includes(s) || descLower.includes(s))) {
            score += 30
            tokenMatched = true
          }
        }
      }

      if (!tokenMatched) {
        allTokensMatched = false
      }
    }

    // Require either strong single match or all tokens matched
    if (score > 0 && (allTokensMatched || score >= 50)) {
      // Small prestige & prize bonus for high-quality ranking
      if (item.prestigeTier === 'T1') score += 10
      else if (item.prestigeTier === 'T2') score += 5
      if (item.prizePool && item.prizePool > 0) score += 5

      scored.push({ item, score })
    }
  }

  // Sort descending by score
  scored.sort((a, b) => b.score - a.score)
  return scored.map((s) => s.item)
}
