import { redirect } from 'next/navigation'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { prisma } from '@/lib/db'

export default async function AdminSubmissionsPage({
  searchParams,
}: {
  searchParams: Promise<{ status?: string }>
}) {
  const params = await searchParams
  const session = await getServerSession(authOptions)
  if ((session?.user as { role?: string })?.role !== 'ADMIN') redirect('/')

  const statusFilter = params.status ?? 'PENDING'

  const submissions = await prisma.organizerSubmission.findMany({
    where: statusFilter === 'all' ? {} : { status: statusFilter as 'PENDING' | 'APPROVED' | 'REJECTED' },
    orderBy: { createdAt: 'desc' },
    take: 50,
  })

  const STATUS_COLOR: Record<string, string> = {
    PENDING:  'text-closing bg-closing/10',
    APPROVED: 'text-open bg-open/10',
    REJECTED: 'text-red-400 bg-red-400/10',
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6 pt-4">
      <div className="flex items-center justify-between">
        <h1 className="font-serif text-3xl text-text-primary">Submissions</h1>
        <div className="flex gap-2">
          {['PENDING', 'APPROVED', 'REJECTED', 'all'].map(s => (
            <a
              key={s}
              href={`/admin/submissions?status=${s}`}
              className={`px-3 py-1 rounded-chip text-xs font-mono border transition-colors ${
                statusFilter === s
                  ? 'border-accent text-accent'
                  : 'border-border text-text-muted hover:border-accent/50'
              }`}
            >
              {s.charAt(0).toUpperCase() + s.slice(1).toLowerCase()}
            </a>
          ))}
        </div>
      </div>

      <div className="bg-card border border-border rounded-card overflow-hidden">
        <table className="w-full text-sm font-mono">
          <thead>
            <tr className="border-b border-border">
              {['Hackathon', 'Org', 'Submitted by', 'Date', 'Status', 'Actions'].map(h => (
                <th key={h} className="text-left px-4 py-3 text-text-muted font-normal text-xs">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {submissions.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-text-muted text-center">
                  No submissions with status: {statusFilter}
                </td>
              </tr>
            ) : submissions.map((sub: any) => (
              <tr key={sub.id} className="border-b border-border last:border-0 hover:bg-tag-bg transition-colors">
                <td className="px-4 py-3 text-text-primary max-w-[200px] truncate">{sub.hackathonTitle}</td>
                <td className="px-4 py-3 text-text-muted max-w-[140px] truncate">{sub.orgName}</td>
                <td className="px-4 py-3 text-text-muted text-xs max-w-[160px] truncate">{sub.submittedBy}</td>
                <td className="px-4 py-3 text-text-muted text-xs">
                  {new Date(sub.createdAt).toLocaleDateString('en-IN')}
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded-chip text-xs ${STATUS_COLOR[sub.status]}`}>
                    {sub.status}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex gap-2">
                    <a
                      href={sub.applyUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-accent hover:underline"
                    >
                      View →
                    </a>
                    {sub.status === 'PENDING' && (
                      <>
                        <span className="text-border">|</span>
                        <span className="text-xs text-text-muted italic">
                          Manual entry required
                        </span>
                      </>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p className="text-xs font-mono text-text-muted">
        v1: Approved submissions are entered into the DB manually. v2 will have a form here.
      </p>
    </div>
  )
}
