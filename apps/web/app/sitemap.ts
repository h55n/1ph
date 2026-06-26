import { prisma } from '@/lib/db'
import { demoHackathons, shouldUseDemoData } from '@/lib/demo-data'

export default async function sitemap() {
  const staticPages = [
    { url: 'https://1ph.dev', lastModified: new Date(), changeFrequency: 'hourly' as const, priority: 1 },
    { url: 'https://1ph.dev/submit', lastModified: new Date(), changeFrequency: 'monthly' as const, priority: 0.3 },
  ]

  const hackathons = shouldUseDemoData()
    ? demoHackathons.filter((h) => h.status !== 'CLOSED').map((h) => ({ slug: h.slug, updatedAt: h.updatedAt }))
    : await prisma.hackathon
    .findMany({
      select: { slug: true, updatedAt: true },
      where: { status: { not: 'CLOSED' } },
      orderBy: { updatedAt: 'desc' },
    })
    .catch(() => [])

  const hackathonPages = hackathons.map((h) => ({
    url: `https://1ph.dev/hackathon/${h.slug}`,
    lastModified: h.updatedAt,
    changeFrequency: 'daily' as const,
    priority: 0.8,
  }))

  return [...staticPages, ...hackathonPages]
}
