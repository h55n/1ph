import { revalidatePath } from 'next/cache'
import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  const authHeader = request.headers.get('authorization') ?? ''
  const token = authHeader.replace('Bearer ', '')

  if (!process.env.REVALIDATE_SECRET || token !== process.env.REVALIDATE_SECRET) {
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
