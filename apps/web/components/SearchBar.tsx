'use client'

import { useRouter, useSearchParams, usePathname } from 'next/navigation'
import { useCallback, useState, useTransition, useRef } from 'react'

export function SearchBar() {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const [value, setValue] = useState(searchParams.get('q') ?? '')
  const [, startTransition] = useTransition()

  const push = useCallback(
    (q: string) => {
      const params = new URLSearchParams(searchParams.toString())
      if (q) params.set('q', q)
      else params.delete('q')
      startTransition(() => router.push(`${pathname}?${params.toString()}`))
    },
    [router, pathname, searchParams]
  )

  // Simple debounce
  const timerRef = useRef<NodeJS.Timeout | null>(null)
  const debouncedPush = useCallback((q: string) => {
    if (timerRef.current) clearTimeout(timerRef.current)
    timerRef.current = setTimeout(() => push(q), 300)
  }, [push])

  return (
    <div className="relative flex-1 max-w-sm">
      <div className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted text-sm pointer-events-none">🔍</div>
      <input
        type="text"
        value={value}
        placeholder="Search hackathons..."
        onChange={(e) => {
          setValue(e.target.value)
          debouncedPush(e.target.value)
        }}
        className="w-full bg-card border border-border rounded-card pl-9 pr-8 py-2 text-sm font-mono text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent transition-colors duration-150"
      />
      {value && (
        <button
          onClick={() => { setValue(''); push('') }}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-primary text-xs"
          aria-label="Clear search"
        >
          ✕
        </button>
      )}
    </div>
  )
}
