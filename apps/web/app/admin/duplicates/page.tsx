import { prisma } from '@/lib/db'

export default async function AdminDuplicatesPage() {
  // Find hackathons with similar titles by fetching all and comparing
  // In production upgrade to Postgres similarity extension
  const hackathons = await prisma.hackathon.findMany({
    select: { id: true, title: true, organizerName: true, source: true, applyUrl: true, slug: true, status: true },
    where: { status: { not: 'CLOSED' } },
    orderBy: { title: 'asc' },
  })

  // Simple duplicate detection: same apply URL across different sources
  const urlMap = new Map<string, typeof hackathons>()
  for (const h of hackathons) {
    const key = h.applyUrl.toLowerCase().trim()
    if (!urlMap.has(key)) urlMap.set(key, [])
    urlMap.get(key)!.push(h)
  }

  const duplicateGroups = [...urlMap.values()].filter((g) => g.length > 1)

  return (
    <div className="space-y-6">
      <h1 className="font-serif text-3xl text-text-primary">
        Duplicates{' '}
        <span className="text-text-muted text-xl">({duplicateGroups.length} groups)</span>
      </h1>

      {duplicateGroups.length === 0 ? (
        <div className="bg-card border border-border rounded-card p-8 text-center">
          <p className="font-mono text-sm text-text-muted">No duplicate apply URLs detected.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {duplicateGroups.map((group, i) => (
            <div key={i} className="bg-card border border-border rounded-card overflow-hidden">
              <div className="px-4 py-2 bg-tag-bg border-b border-border">
                <span className="font-mono text-xs text-closing">Duplicate apply URL: </span>
                <span className="font-mono text-xs text-text-muted truncate">{group[0].applyUrl}</span>
              </div>
              <table className="w-full text-sm font-mono">
                <tbody>
                  {group.map((h) => (
                    <tr key={h.id} className="border-b border-border last:border-0 hover:bg-tag-bg transition-colors">
                      <td className="px-4 py-2 text-text-primary max-w-[200px] truncate">{h.title}</td>
                      <td className="px-4 py-2 text-text-muted text-xs">{h.organizerName}</td>
                      <td className="px-4 py-2 text-text-muted text-xs">{h.source}</td>
                      <td className="px-4 py-2 text-text-muted text-xs">{h.status}</td>
                      <td className="px-4 py-2">
                        <a href={`/hackathon/${h.slug}`} target="_blank" className="text-xs text-accent hover:underline">
                          View →
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}
        </div>
      )}

      <p className="text-xs font-mono text-text-muted">
        Showing duplicates detected by identical apply URL. Delete extras directly in Supabase dashboard.
      </p>
    </div>
  )
}
