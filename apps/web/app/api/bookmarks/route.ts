import { NextRequest, NextResponse } from 'next/server'
import { requireSupabaseUser } from '@/lib/auth'
import { isPrismaErrorCode, logInternalApiError } from '@/lib/api-errors'
import { readHackathonId } from '@/lib/api-validation'
import { prisma } from '@/lib/db'

export async function GET() {
  const session = await requireSupabaseUser()
  if (!session) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

  try {
    const bookmarks = await prisma.bookmark.findMany({
      where: { userId: session.user.id },
      select: { hackathonId: true, createdAt: true },
      orderBy: { createdAt: 'desc' },
    })
    return NextResponse.json({ bookmarks })
  } catch (error) {
    return NextResponse.json(logInternalApiError('list bookmarks', error), { status: 500 })
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
    const bookmark = await prisma.bookmark.create({ data: { userId: session.user.id, hackathonId } })
    return NextResponse.json(bookmark, { status: 201 })
  } catch (error) {
    if (isPrismaErrorCode(error, 'P2002')) {
      return NextResponse.json({ error: 'Already bookmarked' }, { status: 409 })
    }
    if (isPrismaErrorCode(error, 'P2003')) {
      return NextResponse.json({ error: 'Hackathon not found' }, { status: 404 })
    }
    return NextResponse.json(logInternalApiError('create bookmark', error), { status: 500 })
  }
}
