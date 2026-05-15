'use client'

import { useRouter, useSearchParams, usePathname } from 'next/navigation'
import { useState } from 'react'
import { cn } from '@/lib/utils'

const FILTERS = [
  { key: 'theme', label: 'Theme', options: ['AI/ML', 'Web3', 'Fintech', 'Health', 'Open', 'Hardware', 'Social Impact', 'Gaming', 'EdTech'] },
  { key: 'mode', label: 'Mode', options: ['ONLINE', 'OFFLINE', 'HYBRID'], display: { ONLINE: 'Online', OFFLINE: 'In-Person', HYBRID: 'Hybrid' } },
  { key: 'fee', label: 'Entry', options: ['free', 'paid'], display: { free: 'Free', paid: 'Paid' } },
  { key: 'team', label: 'Team', options: ['solo', '2-4', '5+'], display: { solo: 'Solo', '2-4': '2–4', '5+': '5+' } },
  { key: 'eligibility', label: 'Who', options: ['STUDENTS', 'OPEN', 'PROFESSIONALS'], display: { STUDENTS: 'Students', OPEN: 'Open to All', PROFESSIONALS: 'Professionals' } },
  { key: 'duration', label: 'Duration', options: ['HR24', 'HR48', 'WEEK', 'MONTH'], display: { HR24: '24hr', HR48: '48hr', WEEK: 'Week-long', MONTH: 'Month-long' } },
  { key: 'city', label: 'City', options: ['bengaluru', 'mumbai', 'pune', 'delhi', 'hyderabad', 'chennai'], display: { bengaluru: 'Bengaluru', mumbai: 'Mumbai', pune: 'Pune', delhi: 'Delhi NCR', hyderabad: 'Hyderabad', chennai: 'Chennai' } },
]

const SORT_OPTIONS = [
  { value: 'prestige', label: 'Prestige' },
  { value: 'deadline', label: 'Deadline' },
  { value: 'prize', label: 'Prize Pool' },
  { value: 'newest', label: 'Newest' },
]

function getDisplay(filter: typeof FILTERS[0], val: string) {
  if ('display' in filter && (filter as any).display) return ((filter as any).display)[val] ?? val
  return val
}

export function FilterBar() {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const [openDropdown, setOpenDropdown] = useState<string | null>(null)

  function setParam(key: string, value: string | null) {
    const params = new URLSearchParams(searchParams.toString())
    if (value === null || value === searchParams.get(key)) params.delete(key)
    else params.set(key, value)
    params.delete('page') // Reset pagination on filter change
    router.push(`${pathname}?${params.toString()}`)
    setOpenDropdown(null)
  }

  return (
    <div className="flex items-center gap-2 flex-wrap">
      {/* Sort */}
      <div className="relative">
        <button
          onClick={() => setOpenDropdown(openDropdown === 'sort' ? null : 'sort')}
          className={cn(
            'flex items-center gap-1.5 px-3 py-1.5 rounded-card border text-sm font-mono transition-all duration-150',
            searchParams.get('sort') ? 'border-accent text-accent bg-accent/10' : 'border-border text-text-muted hover:border-accent/50 hover:text-text-primary'
          )}
        >
          Sort: {SORT_OPTIONS.find((s) => s.value === (searchParams.get('sort') ?? 'newest'))?.label}
          <span className="text-xs">▾</span>
        </button>
        {openDropdown === 'sort' && (
          <Dropdown onClose={() => setOpenDropdown(null)}>
            {SORT_OPTIONS.map((opt) => (
              <DropdownItem key={opt.value} active={(searchParams.get('sort') ?? 'newest') === opt.value} onClick={() => setParam('sort', opt.value)}>
                {opt.label}
              </DropdownItem>
            ))}
          </Dropdown>
        )}
      </div>

      <div className="w-px h-6 bg-border" />

      {FILTERS.map((filter) => {
        const active = searchParams.get(filter.key)
        return (
          <div key={filter.key} className="relative">
            <button
              onClick={() => setOpenDropdown(openDropdown === filter.key ? null : filter.key)}
              className={cn(
                'flex items-center gap-1.5 px-3 py-1.5 rounded-card border text-sm font-mono transition-all duration-150',
                active ? 'border-accent text-accent bg-accent/10' : 'border-border text-text-muted hover:border-accent/50 hover:text-text-primary'
              )}
            >
              {active ? getDisplay(filter, active) : filter.label}
              <span className="text-xs">▾</span>
            </button>
            {openDropdown === filter.key && (
              <Dropdown onClose={() => setOpenDropdown(null)}>
                {active && <DropdownItem active={false} onClick={() => setParam(filter.key, null)}>✕ Clear</DropdownItem>}
                {filter.options.map((opt) => (
                  <DropdownItem key={opt} active={active === opt} onClick={() => setParam(filter.key, opt)}>
                    {getDisplay(filter, opt)}
                  </DropdownItem>
                ))}
              </Dropdown>
            )}
          </div>
        )
      })}
    </div>
  )
}

function Dropdown({ children, onClose }: { children: React.ReactNode; onClose: () => void }) {
  return (
    <>
      <div className="fixed inset-0 z-10" onClick={onClose} />
      <div className="absolute left-0 top-full mt-1 z-20 min-w-[140px] bg-card border border-border rounded-card shadow-xl overflow-hidden animate-fade-in">
        {children}
      </div>
    </>
  )
}

function DropdownItem({ children, active, onClick }: { children: React.ReactNode; active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={cn('w-full text-left px-3 py-2 text-sm font-mono transition-colors duration-100', active ? 'text-accent bg-accent/10' : 'text-text-muted hover:text-text-primary hover:bg-tag-bg')}
    >
      {children}
    </button>
  )
}
