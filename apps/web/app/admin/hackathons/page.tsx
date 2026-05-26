import { prisma } from '@/lib/db'

export default async function AdminHackathonsPage({
  searchParams,
}: {
  searchParams: Promise<{ source?: string; status?: string; tier?: string }>
}) {
  const params = await searchParams
  const where: any = {}
  if (params.source) where.source = params.source
  if (params.status) where.status = params.status
  if (params.tier) where.prestigeTier = params.tier

  const hackathons = await prisma.hackathon.findMany({
    where,
    orderBy: { createdAt: 'desc' },
    take: 100,
    select: {
      id: true, title: true, organizerName: true, source: true,
      prestigeTier: true, status: true, isVerified: true,
      isFeatured: true, lastSyncedAt: true, urlHealthFails: true,
      registrationClose: true, slug: true,
    },
  })

  const TIER_COLOR: Record<string, string> = { T1: 'text-yellow-400', T2: 'text-slate-300', T3: 'text-text-muted' }
  const STATUS_COLOR: Record<string, string> = { OPEN: 'text-open', CLOSING_SOON: 'text-closing', UPCOMING: 'text-upcoming', CLOSED: 'text-text-muted' }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <h1 className="font-serif text-3xl text-text-primary">
          Hackathons <span className="text-text-muted text-xl">({hackathons.length})</span>
        </h1>
        <div className="flex gap-2 flex-wrap">
          {[{ key: 'status', value: 'OPEN', label: 'Open' }, { key: 'status', value: 'CLOSED', label: 'Closed' }, { key: 'tier', value: 'T1', label: 'T1' }, { key: 'tier', value: 'T2', label: 'T2' }].map((f) => (
            <a key={`${f.key}-${f.value}`} href={`/admin/hackathons?${f.key}=${f.value}`} className="px-3 py-1 rounded-chip text-xs font-mono border border-border text-text-muted hover:border-accent/50 hover:text-text-primary transition-colors">
              {f.label}
            </a>
          ))}
          <a href="/admin/hackathons" className="px-3 py-1 rounded-chip text-xs font-mono border border-border text-text-muted hover:border-accent/50 transition-colors">Clear</a>
        </div>
      </div>

      <div className="bg-card border border-border rounded-card overflow-x-auto">
        <table className="w-full text-sm font-mono min-w-[800px]">
          <thead>
            <tr className="border-b border-border">
              {['Title', 'Organizer', 'Source', 'Tier', 'Status', 'Verified', 'URL Fails', 'Last Sync', 'Actions'].map((col) => (
                <th key={col} className="text-left px-3 py-3 text-text-muted font-normal text-xs whitespace-nowrap">{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {hackathons.map((h: any) => (
              <tr key={h.id} className="border-b border-border last:border-0 hover:bg-tag-bg transition-colors">
                <td className="px-3 py-2 max-w-[200px]"><span className="text-text-primary line-clamp-1">{h.title}</span></td>
                <td className="px-3 py-2 text-text-muted max-w-[120px] truncate">{h.organizerName}</td>
                <td className="px-3 py-2 text-text-muted text-xs">{h.source}</td>
                <td className={`px-3 py-2 text-xs font-bold ${TIER_COLOR[h.prestigeTier]}`}>{h.prestigeTier}</td>
                <td className={`px-3 py-2 text-xs ${STATUS_COLOR[h.status]}`}>{h.status}</td>
                <td className="px-3 py-2 text-xs">{h.isVerified ? <span className="text-open">✓</span> : <span className="text-text-muted">—</span>}</td>
                <td className={`px-3 py-2 text-xs ${h.urlHealthFails > 0 ? 'text-closing' : 'text-text-muted'}`}>{h.urlHealthFails > 0 ? `⚠ ${h.urlHealthFails}` : '0'}</td>
                <td className="px-3 py-2 text-text-muted text-xs whitespace-nowrap">{h.lastSyncedAt ? new Date(h.lastSyncedAt).toLocaleDateString('en-IN') : 'Never'}</td>
                <td className="px-3 py-2"><a href={`/hackathon/${h.slug}`} target="_blank" className="text-xs text-accent hover:underline">View →</a></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
