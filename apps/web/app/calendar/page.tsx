import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { prisma } from '@/lib/db'
import { redirect } from 'next/navigation'
import { HackathonCard } from '@/components/HackathonCard'

export const revalidate = 0

export default async function CalendarPage() {
  const session = await getServerSession(authOptions)
  if (!session?.user) redirect('/login?callbackUrl=/calendar')

  const userId = (session.user as { id: string }).id

  // Fetch registrations
  const registrations = await prisma.registration.findMany({
    where: { userId },
    include: {
      hackathon: {
        select: {
          id: true, slug: true, title: true, organizerName: true, organizerLogoUrl: true,
          prestigeTier: true, status: true, prizePool: true, prizeCurrency: true,
          prizeDescription: true, entryFee: true, entryFeeCurrency: true,
          registrationClose: true, mode: true, themeTags: true, scope: true,
          description: true,
        }
      }
    },
    orderBy: {
      hackathon: {
        eventStart: 'asc', // Sort by upcoming events
      }
    }
  })

  // Fetch bookmarks just to pass to card, though we'll only pass true if it's bookmarked
  const bookmarks = await prisma.bookmark.findMany({
    where: { userId },
    select: { hackathonId: true }
  })
  const bookmarkedIds = new Set(bookmarks.map(b => b.hackathonId))

  if (registrations.length === 0) {
    return (
      <div className="space-y-6">
        <h1 className="font-serif text-3xl text-text-primary">Your Calendar</h1>
        <div className="text-center py-20 border border-border/50 rounded-card bg-card/30">
          <p className="font-serif text-xl text-text-muted mb-2">No registrations yet.</p>
          <p className="text-sm font-mono text-text-muted">Register for hackathons to see them here.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="pt-4 pb-2">
        <h1 className="font-serif text-4xl text-text-primary mb-2">
          Your <span className="text-accent">Calendar</span>
        </h1>
        <p className="text-text-muted font-mono text-sm">
          Track upcoming hackathons you are registered for.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {registrations.map((reg, i) => {
          const h = reg.hackathon
          return (
            <HackathonCard
              key={h.id}
              hackathon={{
                ...h,
                prizePool: h.prizePool ? Number(h.prizePool) : null,
                entryFee: h.entryFee ? Number(h.entryFee) : null,
                registrationClose: h.registrationClose,
              }}
              index={i}
              isRegistered={true}
              isBookmarked={bookmarkedIds.has(h.id)}
            />
          )
        })}
      </div>
    </div>
  )
}
