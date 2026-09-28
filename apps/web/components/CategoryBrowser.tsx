'use client'

import { useRouter, useSearchParams, usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { 
  Sparkles, 
  Cpu, 
  Coins, 
  Gamepad2, 
  Leaf, 
  Activity, 
  GraduationCap, 
  Compass 
} from 'lucide-react'

const CATEGORIES = [
  {
    id: 'AI/ML',
    label: 'AI & Agents',
    count: '160+ Events',
    icon: Sparkles,
    color: 'text-violet-400 bg-violet-500/15 border-violet-500/25',
  },
  {
    id: 'Web3',
    label: 'Web3 & Crypto',
    count: '48 Events',
    icon: Cpu,
    color: 'text-teal-400 bg-teal-500/15 border-teal-500/25',
  },
  {
    id: 'Fintech',
    label: 'Fintech',
    count: '24 Events',
    icon: Coins,
    color: 'text-emerald-400 bg-emerald-500/15 border-emerald-500/25',
  },
  {
    id: 'Gaming',
    label: 'Gaming & VR',
    count: '19 Events',
    icon: Gamepad2,
    color: 'text-rose-400 bg-rose-500/15 border-rose-500/25',
  },
  {
    id: 'Social Impact',
    label: 'Climate & Impact',
    count: '14 Events',
    icon: Leaf,
    color: 'text-green-400 bg-green-500/15 border-green-500/25',
  },
  {
    id: 'Health',
    label: 'Health & Bio',
    count: '12 Events',
    icon: Activity,
    color: 'text-cyan-400 bg-cyan-500/15 border-cyan-500/25',
  },
  {
    id: 'EdTech',
    label: 'Student & EdTech',
    count: '18 Events',
    icon: GraduationCap,
    color: 'text-amber-400 bg-amber-500/15 border-amber-500/25',
  },
  {
    id: 'Open',
    label: 'Open Innovation',
    count: '100+ Events',
    icon: Compass,
    color: 'text-blue-400 bg-blue-500/15 border-blue-500/25',
  },
]

export function CategoryBrowser() {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const activeTheme = searchParams.get('theme')

  function toggleCategory(themeId: string) {
    const params = new URLSearchParams(searchParams.toString())
    if (activeTheme === themeId) {
      params.delete('theme')
    } else {
      params.set('theme', themeId)
    }
    params.delete('page')
    router.push(`${pathname}?${params.toString()}`, { scroll: false })
  }

  return (
    <div className="pt-1 pb-3">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-xs font-mono font-semibold uppercase tracking-wider text-text-muted">
          Browse by Category
        </h2>
        {activeTheme && (
          <button
            onClick={() => {
              const params = new URLSearchParams(searchParams.toString())
              params.delete('theme')
              router.push(`${pathname}?${params.toString()}`, { scroll: false })
            }}
            className="text-xs font-mono text-accent hover:underline"
          >
            Clear category filter
          </button>
        )}
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 sm:gap-3">
        {CATEGORIES.map((cat) => {
          const Icon = cat.icon
          const isActive = activeTheme === cat.id

          return (
            <button
              key={cat.id}
              onClick={() => toggleCategory(cat.id)}
              className={cn(
                'group text-left p-3 rounded-xl border transition-all duration-200 flex items-center gap-3',
                isActive
                  ? 'bg-accent/15 border-accent text-text-primary shadow-sm shadow-accent/15 scale-[1.02]'
                  : 'bg-[#1E1108]/80 hover:bg-[#28170C] border-[#4A2E18]/60 hover:border-accent/40 text-text-muted hover:text-text-primary hover:-translate-y-0.5'
              )}
            >
              <div className={cn(
                'w-9 h-9 rounded-lg border flex items-center justify-center flex-shrink-0 transition-transform duration-300 group-hover:scale-110',
                cat.color
              )}>
                <Icon className="w-4 h-4" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="text-xs sm:text-sm font-semibold text-text-primary truncate group-hover:text-accent transition-colors">
                  {cat.label}
                </div>
                <div className="text-[11px] font-mono text-text-muted truncate">
                  {cat.count}
                </div>
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}
