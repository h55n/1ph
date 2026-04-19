import { cn } from '@/lib/utils'

interface PrestigeBadgeProps {
  tier: 'T1' | 'T2' | 'T3'
  className?: string
}

export function PrestigeBadge({ tier, className }: PrestigeBadgeProps) {
  if (tier === 'T3') return null

  return (
    <span
      className={cn(
        'inline-flex items-center px-1.5 py-0.5 rounded-chip text-xs font-mono font-medium tracking-wider',
        tier === 'T1' && 'bg-yellow-900/40 text-yellow-400 border border-yellow-700/50',
        tier === 'T2' && 'bg-slate-700/40 text-slate-300 border border-slate-600/50',
        className
      )}
    >
      {tier}
    </span>
  )
}
