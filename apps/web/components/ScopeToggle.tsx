'use client'

import { useRouter, useSearchParams, usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'

const TABS = [
  { value: 'all',    label: 'All' },
  { value: 'GLOBAL', label: '🌐 Global' },
  { value: 'INDIA',  label: '🇮🇳 India' },
]

export function ScopeToggle() {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const current = searchParams.get('scope') ?? 'all'

  function handleTab(value: string) {
    const params = new URLSearchParams(searchParams.toString())
    if (value === 'all') params.delete('scope')
    else params.set('scope', value)
    router.push(`${pathname}?${params.toString()}`)
  }

  return (
    <div className="flex items-center gap-1 bg-card border border-border rounded-card p-1">
      {TABS.map(tab => (
        <button
          key={tab.value}
          onClick={() => handleTab(tab.value)}
          className={cn(
            'px-4 py-1.5 rounded-[6px] text-sm font-mono transition-all duration-[120ms]',
            current === tab.value
              ? 'bg-tag-bg text-text-primary border border-border'
              : 'text-text-muted hover:text-text-primary'
          )}
        >
          {tab.label}
        </button>
      ))}
    </div>
  )
}
