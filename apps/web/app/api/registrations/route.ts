import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { prisma } from '@/lib/db'

export async function GET() {
  const session = await getServerSession(authOptions)
  if (!session?.user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

  const registrations = await prisma.registration.findMany({
    where: { userId: (session.user as { id: string }).id },
    select: { hackathonId: true, createdAt: true },
    orderBy: { createdAt: 'desc' },
  })
  return NextResponse.json({ registrations })
}

export async function POST(req: NextRequest) {
  const session = await getServerSession(authOptions)
  if (!session?.user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

  const { hackathonId } = await req.json()
  if (!hackathonId) return NextResponse.json({ error: 'Missing hackathonId' }, { status: 400 })

  const userId = (session.user as { id: string }).id

  try {
    const registration = await prisma.registration.create({ data: { userId, hackathonId } })
    return NextResponse.json(registration, { status: 201 })
  } catch {
    return NextResponse.json({ error: 'Already registered' }, { status: 409 })
  }
}
