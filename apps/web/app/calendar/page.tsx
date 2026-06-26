import { requireSupabaseUser } from '@/lib/auth'
import { prisma } from '@/lib/db'
import { redirect } from 'next/navigation'
import { VisualCalendar } from '@/components/VisualCalendar'

export const revalidate = 0

export default async function CalendarPage() {
  const session = await requireSupabaseUser()
  if (!session) redirect('/login?callbackUrl=/calendar')

  // Fetch registrations
  const registrations = await prisma.registration.findMany({
    where: { userId: session.user.id },
    include: {
      hackathon: {
        select: {
          id: true, slug: true, title: true, organizerName: true, organizerLogoUrl: true,
          prestigeTier: true, status: true, prizePool: true, prizeCurrency: true,
          prizeDescription: true, entryFee: true, entryFeeCurrency: true,
          registrationClose: true, eventStart: true, eventEnd: true, mode: true, themeTags: true, scope: true,
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
    where: { userId: session.user.id },
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

      <VisualCalendar
        events={registrations.map(reg => ({
          ...reg.hackathon,
          prizePool: reg.hackathon.prizePool ? Number(reg.hackathon.prizePool) : null,
          entryFee: reg.hackathon.entryFee ? Number(reg.hackathon.entryFee) : null,
          eventStart: reg.hackathon.eventStart,
          eventEnd: reg.hackathon.eventEnd,
          registrationClose: reg.hackathon.registrationClose
        }))}
      />
    </div>
  )
}
