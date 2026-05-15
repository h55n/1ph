import { redirect } from 'next/navigation'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { prisma } from '@/lib/db'
import { HackathonCard } from '@/components/HackathonCard'

export default async function BookmarksPage() {
  const session = await getServerSession(authOptions)
  if (!session?.user) redirect('/login?callbackUrl=/bookmarks')

  const userId = (session.user as { id: string }).id

  const bookmarks = await prisma.bookmark.findMany({
    where: { userId },
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

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-serif text-3xl text-text-primary mb-1">Saved hackathons</h1>
        <p className="font-mono text-sm text-text-muted">{bookmarks.length} saved</p>
      </div>

      {bookmarks.length === 0 ? (
        <div className="text-center py-20">
          <p className="font-serif text-2xl text-text-muted mb-2">Nothing saved yet.</p>
          <a href="/" className="font-mono text-sm text-accent hover:underline">Browse hackathons →</a>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
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
