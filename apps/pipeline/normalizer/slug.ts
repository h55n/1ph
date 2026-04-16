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
  const suffix = sourceId.replace(/[^a-z0-9]/gi, '').slice(-6).toLowerCase()
  return suffix ? `${base}-${suffix}` : base
}
