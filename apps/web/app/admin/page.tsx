import { prisma } from '@/lib/db'
import { shouldUseDemoData } from '@/lib/demo-data'
import Link from 'next/link'

export default async function AdminPage() {
  const [pendingCount, totalHackathons, recentRuns] = shouldUseDemoData()
    ? [0, 0, []]
    : await Promise.all([
      prisma.organizerSubmission.count({ where: { status: 'PENDING' } }),
      prisma.hackathon.count(),
      prisma.pipelineRun.findMany({
        orderBy: { runAt: 'desc' },
        take: 10,
        select: { source: true, runAt: true, status: true, newCount: true, updatedCount: true, closedCount: true },
      }),
    ])

  const STATUS_COLOR: Record<string, string> = {
    SUCCESS: 'text-open',
    PARTIAL: 'text-closing',
    FAILED: 'text-red-400',
  }

  return (
    <div className="space-y-8">
      <h1 className="font-serif text-3xl text-text-primary">Admin</h1>

      <div className="grid grid-cols-2 gap-3">
        {[
          { label: 'Total Hackathons', value: totalHackathons },
          { label: 'Pending Submissions', value: pendingCount, alert: pendingCount > 0 },
        ].map((stat) => (
          <div key={stat.label} className="bg-card border border-border rounded-card p-4">
            <div className="font-mono text-xs text-text-muted mb-1">{stat.label}</div>
            <div className={`font-serif text-2xl ${stat.alert ? 'text-closing' : 'text-text-primary'}`}>{stat.value}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-3">
        {[
          { href: '/admin/submissions', label: 'Submissions', badge: pendingCount > 0 ? pendingCount : null },
          { href: '/admin/hackathons', label: 'Hackathons', badge: null },
          { href: '/admin/pipeline', label: 'Pipeline Logs', badge: null },
          { href: '/admin/duplicates', label: 'Duplicates', badge: null },
        ].map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className="flex items-center justify-between bg-card border border-border rounded-card px-4 py-3 hover:border-accent transition-colors"
          >
            <span className="font-mono text-sm text-text-primary">{link.label}</span>
            {link.badge && (
              <span className="font-mono text-xs bg-closing/20 text-closing px-2 py-0.5 rounded-chip">{link.badge}</span>
            )}
          </Link>
        ))}
      </div>

      <div>
        <h2 className="font-serif text-xl text-text-primary mb-3">Recent Pipeline Runs</h2>
        <div className="bg-card border border-border rounded-card overflow-hidden">
          <table className="w-full text-sm font-mono">
            <thead>
              <tr className="border-b border-border">
                {['Source', 'Status', 'New', 'Updated', 'Time'].map((h) => (
                  <th key={h} className="text-left px-4 py-2 text-text-muted font-normal">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {recentRuns.length === 0 ? (
                <tr><td colSpan={5} className="px-4 py-6 text-text-muted text-center">No pipeline runs yet</td></tr>
              ) : recentRuns.map((run, i) => (
                <tr key={i} className="border-b border-border last:border-0 hover:bg-tag-bg transition-colors">
                  <td className="px-4 py-2 text-text-primary">{run.source}</td>
                  <td className={`px-4 py-2 ${STATUS_COLOR[run.status] ?? 'text-text-muted'}`}>{run.status}</td>
                  <td className="px-4 py-2 text-text-muted">+{run.newCount}</td>
                  <td className="px-4 py-2 text-text-muted">~{run.updatedCount}</td>
                  <td className="px-4 py-2 text-text-muted text-xs">
                    {new Date(run.runAt).toLocaleString('en-IN', { dateStyle: 'short', timeStyle: 'short' })}
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
