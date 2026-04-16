// apps/pipeline/status-sweep/index.ts
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

export async function runStatusSweep(): Promise<{
  closed: number
  closingSoon: number
  opened: number
  upcoming: number
  urlFlagged: number
}> {
  const now = new Date()
  const sevenDaysFromNow = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000)

  let closed = 0, closingSoon = 0, opened = 0, upcoming = 0, urlFlagged = 0

  // 1. Close expired hackathons
  const closedResult = await prisma.hackathon.updateMany({
    where: {
      registrationClose: { lt: now },
      status: { not: 'CLOSED' },
    },
    data: { status: 'CLOSED' },
  })
  closed = closedResult.count

  // 2. Mark CLOSING_SOON (within 7 days)
  const closingSoonResult = await prisma.hackathon.updateMany({
    where: {
      registrationClose: { gte: now, lte: sevenDaysFromNow },
      status: { not: 'CLOSED' },
    },
    data: { status: 'CLOSING_SOON' },
  })
  closingSoon = closingSoonResult.count

  // 3. Mark UPCOMING (hasn't opened yet)
  const upcomingResult = await prisma.hackathon.updateMany({
    where: {
      registrationOpen: { gt: now },
      status: { not: 'CLOSED' },
    },
    data: { status: 'UPCOMING' },
  })
  upcoming = upcomingResult.count

  // 4. Mark OPEN (everything else that's active)
  const openResult = await prisma.hackathon.updateMany({
    where: {
      registrationClose: { gt: sevenDaysFromNow },
      registrationOpen: { lte: now },
      status: { not: 'CLOSED' },
    },
    data: { status: 'OPEN' },
  })
  opened = openResult.count

  // 5. Auto-close hackathons where URL has failed 7+ consecutive days
  const autoClosedResult = await prisma.hackathon.updateMany({
    where: {
      urlHealthFails: { gte: 7 },
      status: { not: 'CLOSED' },
    },
    data: { status: 'CLOSED' },
  })
  urlFlagged = autoClosedResult.count

  await prisma.$disconnect()

  return { closed, closingSoon, opened, upcoming, urlFlagged }
}
