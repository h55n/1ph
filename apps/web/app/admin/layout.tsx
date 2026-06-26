import { redirect } from 'next/navigation'
import { requireSupabaseUser } from '@/lib/auth'
import Link from 'next/link'

export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  const session = await requireSupabaseUser()
  if (session?.role !== 'ADMIN') redirect('/login?callbackUrl=/admin')

  const NAV = [
    { href: '/admin', label: 'Overview' },
    { href: '/admin/submissions', label: 'Submissions' },
    { href: '/admin/hackathons', label: 'Hackathons' },
    { href: '/admin/pipeline', label: 'Pipeline' },
    { href: '/admin/duplicates', label: 'Duplicates' },
  ]

  return (
    <div className="flex gap-8 pt-4">
      <nav className="w-44 flex-shrink-0 space-y-1">
        <p className="font-mono text-xs text-text-muted uppercase tracking-wider mb-3">Admin</p>
        {NAV.map((n) => (
          <Link
            key={n.href}
            href={n.href}
            className="block px-3 py-2 rounded-card font-mono text-sm text-text-muted hover:text-text-primary hover:bg-tag-bg transition-colors"
          >
            {n.label}
          </Link>
        ))}
      </nav>
      <div className="flex-1 min-w-0">{children}</div>
    </div>
  )
}
