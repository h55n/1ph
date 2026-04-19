import { prisma } from '@/lib/db'

export default async function AdminPipelinePage() {
  const runs = await prisma.pipelineRun.findMany({ orderBy: { runAt: 'desc' }, take: 100 })

  const latestBySource = runs.reduce<Record<string, typeof runs[0]>>((acc, run) => {
    if (!acc[run.source]) acc[run.source] = run
    return acc
  }, {})

  const STATUS_COLOR: Record<string, string> = { SUCCESS: 'text-open', PARTIAL: 'text-closing', FAILED: 'text-red-400' }
  const STATUS_BG: Record<string, string> = { SUCCESS: 'bg-open/10', PARTIAL: 'bg-closing/10', FAILED: 'bg-red-400/10' }

  return (
    <div className="space-y-8">
      <h1 className="font-serif text-3xl text-text-primary">Pipeline Logs</h1>

      <div>
        <h2 className="font-mono text-xs text-text-muted uppercase tracking-wider mb-3">Latest per Source</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
          {Object.entries(latestBySource).map(([source, run]) => (
            <div key={source} className="bg-card border border-border rounded-card p-3">
              <div className="font-mono text-xs text-text-muted mb-1">{source}</div>
              <div className={`font-mono text-sm font-medium ${STATUS_COLOR[run.status]}`}>{run.status}</div>
              <div className="font-mono text-xs text-text-muted mt-1">{new Date(run.runAt).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}</div>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h2 className="font-mono text-xs text-text-muted uppercase tracking-wider mb-3">All Runs (Last 100)</h2>
        <div className="bg-card border border-border rounded-card overflow-x-auto">
          <table className="w-full text-sm font-mono min-w-[640px]">
            <thead>
              <tr className="border-b border-border">
                {['Source', 'Status', 'New', 'Updated', 'Closed', 'Ran at', 'Errors'].map((h) => (
                  <th key={h} className="text-left px-4 py-3 text-text-muted font-normal text-xs">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {runs.map((run) => (
                <tr key={run.id} className="border-b border-border last:border-0 hover:bg-tag-bg transition-colors">
                  <td className="px-4 py-2 text-text-primary">{run.source}</td>
                  <td className="px-4 py-2">
                    <span className={`px-2 py-0.5 rounded-chip text-xs ${STATUS_COLOR[run.status]} ${STATUS_BG[run.status]}`}>{run.status}</span>
                  </td>
                  <td className="px-4 py-2 text-open">+{run.newCount}</td>
                  <td className="px-4 py-2 text-text-muted">~{run.updatedCount}</td>
                  <td className="px-4 py-2 text-text-muted">{run.closedCount}</td>
                  <td className="px-4 py-2 text-text-muted text-xs whitespace-nowrap">
                    {new Date(run.runAt).toLocaleString('en-IN', { dateStyle: 'short', timeStyle: 'short' })}
                  </td>
                  <td className="px-4 py-2 text-red-400 text-xs max-w-[180px] truncate">
                    {run.errorLog ? <span title={run.errorLog}>{run.errorLog.slice(0, 50)}…</span> : <span className="text-text-muted">—</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
