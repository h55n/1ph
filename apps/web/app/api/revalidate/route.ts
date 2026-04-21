import { revalidatePath } from 'next/cache'
import { NextResponse } from 'next/server'
import { timingSafeEqual } from 'node:crypto'

function isAuthorized(authorizationHeader: string, secret: string): boolean {
  const token = authorizationHeader.replace('Bearer ', '').trim()
  const tokenBuf = Buffer.from(token)
  const secretBuf = Buffer.from(secret)
  if (tokenBuf.length !== secretBuf.length) return false
  return timingSafeEqual(tokenBuf, secretBuf)
}

export async function POST(request: Request) {
  const authHeader = request.headers.get('authorization') ?? ''
  const secret = process.env.REVALIDATE_SECRET

  if (!secret) return NextResponse.json({ error: 'Not configured' }, { status: 500 })
  if (!isAuthorized(authHeader, secret)) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

  revalidatePath('/', 'layout')  // revalidates all pages
  revalidatePath('/hackathon/[slug]', 'page')
  revalidatePath('/sitemap.xml')

  return NextResponse.json({ revalidated: true })
}
