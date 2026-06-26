import { NextRequest, NextResponse } from 'next/server'
import { requireSupabaseUser } from '@/lib/auth'
import { prisma } from '@/lib/db'

export async function DELETE(
  _req: NextRequest,
  { params }: { params: Promise<{ hackathonId: string }> }
) {
  const { hackathonId } = await params
  const session = await requireSupabaseUser()
  if (!session) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

  try {
    await prisma.bookmark.delete({
      where: { userId_hackathonId: { userId: session.user.id, hackathonId } },
    })
    return NextResponse.json({ deleted: true })
  } catch {
    return NextResponse.json({ error: 'Not found' }, { status: 404 })
  }
}
