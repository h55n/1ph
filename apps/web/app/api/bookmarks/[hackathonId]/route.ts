import { NextRequest, NextResponse } from 'next/server'
import { requireSupabaseUser } from '@/lib/auth'
import { isPrismaErrorCode, logInternalApiError } from '@/lib/api-errors'
import { normalizeHackathonId } from '@/lib/api-validation'
import { prisma } from '@/lib/db'

export async function DELETE(
  _req: NextRequest,
  { params }: { params: Promise<{ hackathonId: string }> }
) {
  const { hackathonId: rawHackathonId } = await params
  const hackathonId = normalizeHackathonId(rawHackathonId)
  if (!hackathonId) return NextResponse.json({ error: 'Invalid hackathonId' }, { status: 400 })

  const session = await requireSupabaseUser()
  if (!session) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

  try {
    await prisma.bookmark.delete({
      where: { userId_hackathonId: { userId: session.user.id, hackathonId } },
    })
    return NextResponse.json({ deleted: true })
  } catch (error) {
    if (isPrismaErrorCode(error, 'P2025')) {
      return NextResponse.json({ error: 'Not found' }, { status: 404 })
    }
    return NextResponse.json(logInternalApiError('delete bookmark', error), { status: 500 })
  }
}
