// apps/pipeline/tier-engine/t1-orgs.ts
// SINGLE SOURCE OF TRUTH for T1 org list
// Update only here — never inline in other files

export const T1_ORGS: string[] = [
  // Global tech
  'google', 'meta', 'facebook', 'microsoft', 'amazon', 'aws',
  'github', 'nasa', 'openai', 'anthropic', 'deepmind',
  'goldman sachs', 'jpmorgan', 'jp morgan', 'morgan stanley',
  'ethereum foundation', 'polygon', 'solana foundation',
  'united nations', 'un women', 'unicef',

  // India — government & nationals
  'nasscom', 'dpiit', 'startup india', 'smart india hackathon', 'sih',
  'isro', 'nic', 'meity', 'ministry of electronics',
  'government of india', 'govt of india',

  // India — corporate
  'flipkart', 'walmart global tech', 'walmart labs',
  'infosys', 'tata consultancy', 'tcs', 'wipro',
  'razorpay', 'zerodha', 'cred', 'swiggy', 'zomato',

  // IIT-organized national hackathons
  // Matched by keyword check in tier-engine/index.ts
  // 'iit bombay', 'iit delhi', 'iit madras', ...
  // → handled by iitNationalCheck() function below
]

// Keyword check for IIT/NIT national hackathons
// Only matches if the hackathon title indicates a national scope
export function isIITNationalHackathon(title: string, organizerName: string): boolean {
  const combined = `${title} ${organizerName}`.toLowerCase()
  const isIIT = /\biit\b|\biiit\b|\bnit\b|\bbits\b/.test(combined)
  const isNational = /national|india|pan.india|nationwide/.test(combined)
  return isIIT && isNational
}
