export function SkeletonCard() {
  return (
    <div className="bg-[#27150A]/70 border border-[#4A2E18]/60 rounded-card overflow-hidden flex flex-col animate-pulse">
      {/* Visual Banner placeholder */}
      <div className="h-36 sm:h-40 bg-tag-bg/50 relative">
        {/* Calendar badge placeholder */}
        <div className="absolute top-3 left-3 w-12 h-12 rounded-xl bg-tag-bg/80 border border-white/5" />
        {/* Action badge placeholder */}
        <div className="absolute top-3 right-3 flex items-center gap-1.5">
          <div className="w-8 h-8 rounded-full bg-tag-bg/80 border border-white/5" />
          <div className="w-8 h-8 rounded-full bg-tag-bg/80 border border-white/5" />
        </div>
      </div>

      {/* Body content */}
      <div className="p-4 sm:p-5 flex flex-col flex-1 justify-between gap-3">
        <div className="flex flex-col gap-2.5">
          {/* Status + Time */}
          <div className="flex items-center justify-between">
            <div className="w-16 h-4 bg-tag-bg rounded-full" />
            <div className="w-20 h-3 bg-tag-bg rounded" />
          </div>

          {/* Title */}
          <div className="w-5/6 h-5 bg-tag-bg rounded" />
          <div className="w-3/5 h-5 bg-tag-bg rounded mb-1" />

          {/* Host */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-5 h-5 rounded-full bg-tag-bg" />
              <div className="w-28 h-3.5 bg-tag-bg rounded" />
            </div>
            <div className="w-14 h-4 bg-tag-bg rounded-full" />
          </div>

          {/* Location */}
          <div className="w-24 h-3 bg-tag-bg rounded" />
        </div>

        {/* Footer */}
        <div className="pt-3 border-t border-[#4A2E18]/60 flex items-center justify-between">
          <div className="w-24 h-6 bg-tag-bg rounded-full" />
          <div className="w-16 h-5 bg-tag-bg rounded-full" />
        </div>
      </div>
    </div>
  )
}

export function SkeletonGrid({ count = 12 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
      {Array.from({ length: count }).map((_, i) => <SkeletonCard key={i} />)}
    </div>
  )
}
