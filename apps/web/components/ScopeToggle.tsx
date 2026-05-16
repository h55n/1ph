'use client'

import { useRouter, useSearchParams, usePathname } from 'next/navigation'
import { useTransition, useOptimistic } from 'react'
import { cn } from '@/lib/utils'
import { motion } from 'framer-motion'

const TABS = [
  { value: 'all',    label: 'All' },
  { value: 'GLOBAL', label: '🌐 Global' },
  { value: 'INDIA',  label: '🇮🇳 India' },
]

export function ScopeToggle() {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const [isPending, startTransition] = useTransition()
  const currentParam = searchParams.get('scope') ?? 'all'
  const [optimisticScope, setOptimisticScope] = useOptimistic(
    currentParam,
    (_state, newScope: string) => newScope
  )

  function handleTab(value: string) {
    setOptimisticScope(value)
    const params = new URLSearchParams(searchParams.toString())
    if (value === 'all') params.delete('scope')
    else params.set('scope', value)
    params.delete('page')
    startTransition(() => {
      router.push(`${pathname}?${params.toString()}`, { scroll: false })
    })
  }

  return (
    <div className="relative flex items-center bg-card border border-border rounded-card p-1">
      {TABS.map((tab) => {
        const isActive = optimisticScope === tab.value
        return (
          <button
            key={tab.value}
            onClick={() => handleTab(tab.value)}
            className={cn(
              'relative px-4 py-1.5 z-10 text-sm font-mono transition-colors duration-300',
              isActive ? 'text-text-primary' : 'text-text-muted hover:text-text-primary'
            )}
          >
            {isActive && (
              <motion.div
                layoutId="active-pill"
                className="absolute inset-0 bg-tag-bg border border-border rounded-[6px] z-[-1]"
                transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
              />
            )}
            {tab.label}
          </button>
        )
      })}
    </div>
  )
}
