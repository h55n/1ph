import { NextRequest, NextResponse } from 'next/server'
import { requireSupabaseUser } from '@/lib/auth'
import { prisma } from '@/lib/db'

export async function GET() {
  const session = await requireSupabaseUser()
  if (!session) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

  const registrations = await prisma.registration.findMany({
    where: { userId: session.user.id },
    select: { hackathonId: true, createdAt: true },
    orderBy: { createdAt: 'desc' },
  })
  return NextResponse.json({ registrations })
}

export async function POST(req: NextRequest) {
  const session = await requireSupabaseUser()
  if (!session) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

  const { hackathonId } = await req.json()
  if (!hackathonId) return NextResponse.json({ error: 'Missing hackathonId' }, { status: 400 })

  try {
    const registration = await prisma.registration.create({ data: { userId: session.user.id, hackathonId } })
    return NextResponse.json(registration, { status: 201 })
  } catch {
    return NextResponse.json({ error: 'Already registered' }, { status: 409 })
  }
}
