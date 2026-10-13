import { NextRequest, NextResponse } from 'next/server'
import { requireSupabaseUser } from '@/lib/auth'
import { isPrismaErrorCode, logInternalApiError } from '@/lib/api-errors'
import { readHackathonId } from '@/lib/api-validation'
import { prisma } from '@/lib/db'

export async function GET() {
  const session = await requireSupabaseUser()
  if (!session) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

  try {
    const registrations = await prisma.registration.findMany({
      where: { userId: session.user.id },
      select: { hackathonId: true, createdAt: true },
      orderBy: { createdAt: 'desc' },
    })
    return NextResponse.json({ registrations })
  } catch (error) {
    return NextResponse.json(logInternalApiError('list registrations', error), { status: 500 })
  }
}

export async function POST(req: NextRequest) {
  const session = await requireSupabaseUser()
  if (!session) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

  const hackathonId = await readHackathonId(req)
  if (!hackathonId) {
    return NextResponse.json({ error: 'Invalid hackathonId' }, { status: 400 })
  }

  try {
    const registration = await prisma.registration.create({ data: { userId: session.user.id, hackathonId } })
    return NextResponse.json(registration, { status: 201 })
  } catch (error) {
    if (isPrismaErrorCode(error, 'P2002')) {
      return NextResponse.json({ error: 'Already registered' }, { status: 409 })
    }
    if (isPrismaErrorCode(error, 'P2003')) {
      return NextResponse.json({ error: 'Hackathon not found' }, { status: 404 })
    }
    return NextResponse.json(logInternalApiError('create registration', error), { status: 500 })
  }
}
