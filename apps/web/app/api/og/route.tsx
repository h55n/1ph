import { ImageResponse } from '@vercel/og'
import { NextRequest } from 'next/server'
import { prisma } from '@/lib/db'

export const runtime = 'nodejs'

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url)
  const slug = searchParams.get('slug')

  let title = 'Every hackathon. One place.'
  let organizer = '1ph'
  let deadline = ''

  if (slug) {
    const h = await prisma.hackathon.findUnique({
      where: { slug },
      select: { title: true, organizerName: true, registrationClose: true },
    })
    if (h) {
      title = h.title
      organizer = h.organizerName
      deadline = `Closes ${new Date(h.registrationClose).toLocaleDateString('en-IN', {
        day: 'numeric', month: 'short', year: 'numeric',
      })}`
    }
  }

  return new ImageResponse(
    (
      <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', padding: '60px', background: '#26150B' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontFamily: 'serif', fontSize: '28px', color: '#F5EDE3' }}>1ph</span>
          {deadline && <span style={{ fontFamily: 'monospace', fontSize: '16px', color: '#E8C468', marginLeft: 'auto' }}>{deadline}</span>}
        </div>
        <div>
          <p style={{ fontFamily: 'monospace', fontSize: '18px', color: '#9E8A7A', marginBottom: '16px' }}>{organizer}</p>
          <h1 style={{ fontFamily: 'serif', fontSize: title.length > 40 ? '38px' : '52px', color: '#F5EDE3', lineHeight: 1.15, margin: 0 }}>{title}</h1>
        </div>
        <span style={{ fontFamily: 'monospace', fontSize: '14px', color: '#91B2DD' }}>1ph.dev — Every hackathon. One place.</span>
      </div>
    ),
    { width: 1200, height: 630 }
  )
}
