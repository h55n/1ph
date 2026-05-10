import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { prisma } from '@/lib/db'

export async function GET() {
  const session = await getServerSession(authOptions)
  if (!session?.user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

  const bookmarks = await prisma.bookmark.findMany({
    where: { userId: (session.user as { id: string }).id },
    select: { hackathonId: true, createdAt: true },
    orderBy: { createdAt: 'desc' },
  })
  return NextResponse.json({ bookmarks })
}

export async function POST(req: NextRequest) {
  const session = await getServerSession(authOptions)
  if (!session?.user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

  const { hackathonId } = await req.json()
  if (!hackathonId) return NextResponse.json({ error: 'Missing hackathonId' }, { status: 400 })

  const userId = (session.user as { id: string }).id

  try {
    const bookmark = await prisma.bookmark.create({ data: { userId, hackathonId } })
    return NextResponse.json(bookmark, { status: 201 })
  } catch {
    return NextResponse.json({ error: 'Already bookmarked' }, { status: 409 })
  }
}
