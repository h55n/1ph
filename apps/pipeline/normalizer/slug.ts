// apps/pipeline/normalizer/slug.ts

export function generateSlug(title: string, sourceId: string): string {
  const base = title
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .trim()
    .slice(0, 60)

  // Append last 6 chars of sourceId for uniqueness
  const sanitized = sourceId.replace(/[^a-z0-9]/gi, '').toLowerCase()
  const fallback = Buffer.from(sourceId || title).toString('hex').slice(-6)
  const suffix = (sanitized.slice(-6) || fallback).toLowerCase()
  return suffix ? `${base}-${suffix}` : base
}
