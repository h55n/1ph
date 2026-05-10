import { formatDistanceToNowStrict } from 'date-fns'

export function formatDeadline(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date
  if (isNaN(d.getTime())) return '—'
  if (d.getFullYear() >= 2099) return 'Ongoing'
  const now = new Date()
  if (d < now) return 'Closed'
  return formatDistanceToNowStrict(d, { addSuffix: true })
    .replace('in ', '').replace(' days', 'd').replace(' day', 'd')
    .replace(' hours', 'h').replace(' hour', 'h')
    .replace(' months', 'mo').replace(' month', 'mo') + ' left'
}

export function formatPrize(pool: number | null | undefined, currency: string | null | undefined): string {
  if (!pool) return 'No prize listed'
  const c = currency?.toUpperCase() ?? 'USD'
  if (c === 'INR') {
    if (pool >= 100000) return `₹${(pool / 100000).toFixed(pool % 100000 === 0 ? 0 : 1)}L`
    return `₹${(pool / 1000).toFixed(0)}K`
  }
  if (pool >= 1000000) return `$${(pool / 1000000).toFixed(1)}M`
  if (pool >= 1000) return `$${(pool / 1000).toFixed(0)}K`
  return `$${pool}`
}

export function formatFee(fee: number | null | undefined, currency: string | null | undefined): string {
  if (!fee) return 'FREE'
  const c = currency?.toUpperCase() ?? 'USD'
  if (c === 'INR') return `₹${fee}`
  return `$${fee}`
}

export function generateSlug(title: string): string {
  return title.toLowerCase().replace(/[^a-z0-9\s-]/g, '').replace(/\s+/g, '-').replace(/-+/g, '-').trim()
}
