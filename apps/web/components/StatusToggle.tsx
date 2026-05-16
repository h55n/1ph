'use client'

import { useRouter, useSearchParams, usePathname } from 'next/navigation'
import { useTransition, useOptimistic } from 'react'
import { cn } from '@/lib/utils'
import { motion } from 'framer-motion'

export function StatusToggle() {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const [isPending, startTransition] = useTransition()
  
  const currentParam = searchParams.get('status') === 'CLOSED'
  const [optimisticClosed, setOptimisticClosed] = useOptimistic(
    currentParam,
    (_state, newStatus: boolean) => newStatus
  )

  function toggle(closed: boolean) {
    setOptimisticClosed(closed)
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
    <div className="relative flex items-center bg-card border border-border rounded-card p-1 max-w-fit">
      <button
        onClick={() => toggle(false)}
        className={cn(
          'relative px-4 py-1.5 z-10 text-sm font-mono transition-colors duration-300',
          !optimisticClosed ? 'text-accent' : 'text-text-muted hover:text-text-primary'
        )}
      >
        {!optimisticClosed && (
          <motion.div
            layoutId="status-pill"
            className="absolute inset-0 bg-accent/10 border border-accent/20 rounded-[6px] z-[-1]"
            transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
          />
        )}
        Open
      </button>
      <button
        onClick={() => toggle(true)}
        className={cn(
          'relative px-4 py-1.5 z-10 text-sm font-mono transition-colors duration-300',
          optimisticClosed ? 'text-text-primary' : 'text-text-muted hover:text-text-primary'
        )}
      >
        {optimisticClosed && (
          <motion.div
            layoutId="status-pill"
            className="absolute inset-0 bg-tag-bg border border-border rounded-[6px] z-[-1]"
            transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
          />
        )}
        Closed
      </button>
    </div>
  )
}
