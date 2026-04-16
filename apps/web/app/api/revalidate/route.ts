import { revalidatePath } from 'next/cache'
import { NextResponse } from 'next/server'
import { timingSafeEqual } from 'node:crypto'

function isAuthorized(authorizationHeader: string, secret: string): boolean {
  const normalizedHeader = authorizationHeader.trim()
  if (!normalizedHeader.startsWith('Bearer ')) {
    return false
  }

  const token = normalizedHeader.slice('Bearer '.length).trim()
  const tokenBuffer = Buffer.from(token)
  const secretBuffer = Buffer.from(secret)

  if (tokenBuffer.length !== secretBuffer.length) {
    return false
  }

  return timingSafeEqual(tokenBuffer, secretBuffer)
}

export async function POST(request: Request) {
  const authHeader = request.headers.get('authorization') ?? ''
  const secret = process.env.REVALIDATE_SECRET

  if (!secret) {
    console.error('REVALIDATE_SECRET is not configured')
    return NextResponse.json({ revalidated: false, error: 'Unauthorized' }, { status: 401 })
  }

  if (!isAuthorized(authHeader, secret)) {
    return NextResponse.json({ revalidated: false, error: 'Unauthorized' }, { status: 401 })
  }

  revalidatePath('/')
  revalidatePath('/hackathon/[slug]', 'page')
  revalidatePath('/sitemap.xml')

  return NextResponse.json({
    revalidated: true,
    paths: ['/', '/hackathon/[slug]', '/sitemap.xml'],
  })
}
