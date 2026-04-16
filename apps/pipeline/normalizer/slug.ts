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
  const sourceSeed = sourceId?.trim() ? sourceId : title
  const sanitized = sourceSeed.replace(/[^a-z0-9]/gi, '').toLowerCase()
  // Hex fallback guarantees a deterministic suffix even when source IDs are all symbols/non-Latin.
  const fallback = Buffer.from(sourceSeed).toString('hex').slice(-6)
  const suffix = (sanitized.slice(-6) || fallback).toLowerCase()
  return suffix ? `${base}-${suffix}` : base
}
