import { redirect } from 'next/navigation'
import { requireSupabaseUser } from '@/lib/auth'
import { prisma } from '@/lib/db'
import { HackathonCard } from '@/components/HackathonCard'

export const dynamic = 'force-dynamic'

export default async function BookmarksPage() {
  const session = await requireSupabaseUser()
  if (!session) redirect('/login?callbackUrl=/bookmarks')

  let bookmarks: any[] = []
  try {
    bookmarks = await prisma.bookmark.findMany({
      where: { userId: session.user.id },
      include: {
        hackathon: {
          select: {
            id: true, slug: true, title: true, organizerName: true, organizerLogoUrl: true,
            prestigeTier: true, status: true, prizePool: true, prizeCurrency: true,
            prizeDescription: true, entryFee: true, entryFeeCurrency: true,
            registrationClose: true, mode: true, themeTags: true, scope: true,
          },
        },
      },
      orderBy: { createdAt: 'desc' },
    })
  } catch (error) {
    console.error('Bookmarks DB lookup error:', error)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-serif text-3xl text-text-primary mb-1">Saved hackathons</h1>
        <p className="font-mono text-sm text-text-muted">{bookmarks.length} saved</p>
      </div>

      {bookmarks.length === 0 ? (
        <div className="text-center py-20 border border-border/40 rounded-card bg-card/20">
          <p className="font-serif text-2xl text-text-muted mb-2">Nothing saved yet.</p>
          <a href="/" className="font-mono text-sm text-accent hover:underline">Browse hackathons →</a>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 sm:gap-6">
          {bookmarks.map(({ hackathon }, i) => (
            <HackathonCard
              key={hackathon.slug}
              hackathon={{
                ...hackathon,
                prizePool: hackathon.prizePool ? Number(hackathon.prizePool) : null,
                entryFee: hackathon.entryFee ? Number(hackathon.entryFee) : null,
              }}
              index={i}
              isBookmarked={true}
            />
          ))}
        </div>
      )}
    </div>
  )
}
