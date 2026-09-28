import { cn } from '@/lib/utils'
import { Sparkles, Award } from 'lucide-react'

interface PrestigeBadgeProps {
  tier: 'T1' | 'T2' | 'T3'
  className?: string
}

export function PrestigeBadge({ tier, className }: PrestigeBadgeProps) {
  if (tier === 'T3') return null

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono font-bold tracking-wider uppercase backdrop-blur-md shadow-sm',
        tier === 'T1' && 'bg-amber-500/20 text-amber-300 border border-amber-500/35 shadow-amber-500/10',
        tier === 'T2' && 'bg-slate-500/20 text-slate-200 border border-slate-400/30',
        className
      )}
    >
      {tier === 'T1' ? <Sparkles className="w-3 h-3 text-amber-400" /> : <Award className="w-3 h-3 text-slate-300" />}
      {tier}
    </span>
  )
}
