export function SkeletonCard() {
  return (
    <div className="bg-card border border-border rounded-card p-5 animate-pulse">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-sm bg-tag-bg" />
          <div className="w-24 h-3 bg-tag-bg rounded" />
        </div>
        <div className="w-8 h-4 bg-tag-bg rounded-chip" />
      </div>
      <div className="w-3/4 h-5 bg-tag-bg rounded mb-2" />
      <div className="w-1/2 h-5 bg-tag-bg rounded mb-4" />
      <div className="flex items-center justify-between mb-4">
        <div className="w-12 h-3 bg-tag-bg rounded" />
        <div className="w-16 h-3 bg-tag-bg rounded" />
      </div>
      <div className="flex gap-3 mb-4">
        <div className="w-16 h-8 bg-tag-bg rounded" />
        <div className="w-px h-8 bg-border" />
        <div className="w-16 h-8 bg-tag-bg rounded" />
      </div>
      <div className="flex gap-2">
        <div className="w-16 h-5 bg-tag-bg rounded-chip" />
        <div className="w-20 h-5 bg-tag-bg rounded-chip" />
      </div>
    </div>
  )
}

export function SkeletonGrid({ count = 9 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {Array.from({ length: count }).map((_, i) => <SkeletonCard key={i} />)}
    </div>
  )
}
