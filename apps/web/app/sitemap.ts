import { prisma } from '@/lib/db'

export default async function sitemap() {
  const staticPages = [
    { url: 'https://1ph.dev', lastModified: new Date(), changeFrequency: 'hourly' as const, priority: 1 },
    { url: 'https://1ph.dev/submit', lastModified: new Date(), changeFrequency: 'monthly' as const, priority: 0.3 },
  ]

  const hackathons = await prisma.hackathon
    .findMany({
      select: { slug: true, updatedAt: true },
      where: { status: { not: 'CLOSED' } },
      orderBy: { updatedAt: 'desc' },
    })
    .catch((error) => {
      console.error('Failed to generate sitemap hackathon entries:', error)
      return []
    })

  const hackathonPages = hackathons.map((h: any) => ({
    url: `https://1ph.dev/hackathon/${h.slug}`,
    lastModified: h.updatedAt,
    changeFrequency: 'daily' as const,
    priority: 0.8,
  }))

  return [...staticPages, ...hackathonPages]
}
