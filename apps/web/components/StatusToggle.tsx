'use client'

import { useRouter, useSearchParams, usePathname } from 'next/navigation'
import { useTransition } from 'react'
import { cn } from '@/lib/utils'

export function StatusToggle() {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const [isPending, startTransition] = useTransition()
  const isClosedView = searchParams.get('status') === 'CLOSED'

  function toggle(closed: boolean) {
    const params = new URLSearchParams(searchParams.toString())
    if (closed) {
      params.set('status', 'CLOSED')
    } else {
      params.delete('status')
    }
    params.delete('page') // Reset pagination on status change
    startTransition(() => {
      router.push(`${pathname}?${params.toString()}`, { scroll: false })
    })
  }

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={() => toggle(false)}
        className={cn(
          'px-3 py-1 rounded-chip text-xs font-mono border transition-all duration-150',
          !isClosedView
            ? 'border-accent text-accent bg-accent/10'
            : 'border-border text-text-muted hover:text-text-primary'
        )}
      >
        Open
      </button>
      <button
        onClick={() => toggle(true)}
        className={cn(
          'px-3 py-1 rounded-chip text-xs font-mono border transition-all duration-150',
          isClosedView
            ? 'border-border text-text-muted bg-tag-bg'
            : 'border-border text-text-muted hover:text-text-primary'
        )}
      >
        Closed
      </button>
    </div>
  )
}
