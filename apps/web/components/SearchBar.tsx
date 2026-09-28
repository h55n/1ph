'use client'

import { useRouter, useSearchParams, usePathname } from 'next/navigation'
import { useCallback, useState, useTransition, useRef, useEffect } from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { Search, X, Sparkles, Trophy, ArrowRight, CornerDownLeft } from 'lucide-react'
import { demoHackathons } from '@/lib/demo-data'
import { smartSearchHackathons } from '@/lib/smart-search'
import { cn } from '@/lib/utils'

const QUICK_SEARCH_CHIPS = [
  { label: '⚡ Generative AI', query: 'ai' },
  { label: '🪙 Web3 & Solana', query: 'web3 solana' },
  { label: '🏆 $100K+ Prizes', query: '100k' },
  { label: '📍 Bengaluru', query: 'bengaluru' },
  { label: '📍 Delhi NCR', query: 'delhi' },
  { label: '✨ Free Entry', query: 'free' },
  { label: '🌐 Online', query: 'online' },
]

export function SearchBar() {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const [value, setValue] = useState(searchParams.get('q') ?? '')
  const [isOpen, setIsOpen] = useState(false)
  const [selectedIndex, setSelectedIndex] = useState(-1)
  const [, startTransition] = useTransition()
  const inputRef = useRef<HTMLInputElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  // Keep local value in sync with URL
  useEffect(() => {
    setValue(searchParams.get('q') ?? '')
  }, [searchParams])

  // Global keyboard shortcut: Cmd+K / Ctrl+K / '/'
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        inputRef.current?.focus()
        setIsOpen(true)
      } else if (e.key === '/' && document.activeElement?.tagName !== 'INPUT' && document.activeElement?.tagName !== 'TEXTAREA') {
        e.preventDefault()
        inputRef.current?.focus()
        setIsOpen(true)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  // Close suggestions when clicking outside
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const pushQuery = useCallback(
    (q: string) => {
      const params = new URLSearchParams(searchParams.toString())
      if (q.trim()) params.set('q', q.trim())
      else params.delete('q')
      params.delete('page')
      startTransition(() => router.push(`${pathname}?${params.toString()}`, { scroll: false }))
    },
    [router, pathname, searchParams]
  )

  // Debounced push
  const timerRef = useRef<NodeJS.Timeout | null>(null)
  const debouncedPush = useCallback(
    (q: string) => {
      if (timerRef.current) clearTimeout(timerRef.current)
      timerRef.current = setTimeout(() => pushQuery(q), 250)
    },
    [pushQuery]
  )

  // Instant smart matches for suggestions popover
  const suggestions = value.trim().length >= 2 
    ? smartSearchHackathons(demoHackathons, value).slice(0, 5)
    : []

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      setIsOpen(false)
      inputRef.current?.blur()
    } else if (e.key === 'ArrowDown') {
      e.preventDefault()
      setSelectedIndex((prev) => (prev < suggestions.length - 1 ? prev + 1 : prev))
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setSelectedIndex((prev) => (prev > -1 ? prev - 1 : -1))
    } else if (e.key === 'Enter') {
      e.preventDefault()
      if (selectedIndex >= 0 && suggestions[selectedIndex]) {
        router.push(`/hackathon/${suggestions[selectedIndex].slug}`)
        setIsOpen(false)
      } else {
        pushQuery(value)
        setIsOpen(false)
      }
    }
  }

  return (
    <div ref={containerRef} className="relative flex-1 max-w-xl">
      {/* Search Input Container */}
      <div className="relative flex items-center">
        <div className="absolute left-3.5 text-text-muted/70 pointer-events-none flex items-center">
          <Search className="w-4 h-4 text-text-muted" />
        </div>

        <input
          ref={inputRef}
          type="text"
          value={value}
          placeholder="Search by topic, organizer, city, or tech stack..."
          onFocus={() => setIsOpen(true)}
          onChange={(e) => {
            const val = e.target.value
            setValue(val)
            debouncedPush(val)
            setIsOpen(true)
            setSelectedIndex(-1)
          }}
          onKeyDown={handleKeyDown}
          className="w-full bg-[#1A1009]/90 border border-[#4A2E18]/80 hover:border-accent/50 focus:border-accent rounded-xl pl-10 pr-24 py-2.5 text-sm font-sans text-text-primary placeholder:text-text-muted/60 focus:outline-none focus:ring-1 focus:ring-accent/40 shadow-sm transition-all duration-200"
        />

        {/* Right side controls: Clear or Keyboard shortcut badge */}
        <div className="absolute right-3 flex items-center gap-1.5">
          {value ? (
            <button
              onClick={() => {
                setValue('')
                pushQuery('')
                setIsOpen(false)
                inputRef.current?.focus()
              }}
              className="w-5 h-5 rounded-full bg-white/10 hover:bg-white/20 text-text-muted hover:text-white flex items-center justify-center text-xs transition-colors"
              aria-label="Clear search"
            >
              <X className="w-3 h-3" />
            </button>
          ) : (
            <kbd className="hidden sm:inline-flex items-center gap-0.5 px-1.5 py-0.5 text-[10px] font-mono text-text-muted/70 bg-white/5 border border-white/10 rounded">
              <span>⌘</span>K
            </kbd>
          )}
        </div>
      </div>

      {/* Quick Search Chips under input */}
      <div className="flex items-center gap-1.5 overflow-x-auto py-2 scrollbar-none text-xs">
        {QUICK_SEARCH_CHIPS.map((chip) => (
          <button
            key={chip.label}
            onClick={() => {
              setValue(chip.query)
              pushQuery(chip.query)
              setIsOpen(false)
            }}
            className={cn(
              'px-2.5 py-1 rounded-full text-xs font-mono whitespace-nowrap transition-all border flex-shrink-0',
              value.toLowerCase() === chip.query
                ? 'bg-accent/20 border-accent text-accent'
                : 'bg-[#1E1108]/60 border-[#4A2E18]/60 text-text-muted hover:text-text-primary hover:border-accent/40'
            )}
          >
            {chip.label}
          </button>
        ))}
      </div>

      {/* Live Smart Suggestions Dropdown */}
      {isOpen && suggestions.length > 0 && (
        <div className="absolute top-12 left-0 right-0 z-50 bg-[#1E1108]/95 backdrop-blur-xl border border-white/15 rounded-2xl shadow-2xl shadow-black/80 overflow-hidden divide-y divide-white/5 animate-fade-in">
          <div className="px-3.5 py-2 text-[11px] font-mono uppercase tracking-wider text-text-muted flex items-center justify-between">
            <span className="flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-accent" />
              Smart Matches
            </span>
            <span>Use ↑↓ to navigate</span>
          </div>

          <div className="max-h-[340px] overflow-y-auto">
            {suggestions.map((h, i) => {
              const isSelected = i === selectedIndex
              return (
                <Link
                  key={h.id}
                  href={`/hackathon/${h.slug}`}
                  onClick={() => setIsOpen(false)}
                  className={cn(
                    'flex items-center justify-between gap-3 p-3 transition-colors',
                    isSelected ? 'bg-accent/15 text-white' : 'hover:bg-white/[0.04] text-text-primary'
                  )}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    {/* Small thumbnail */}
                    {h.coverImageUrl ? (
                      <div className="w-10 h-10 rounded-lg overflow-hidden relative flex-shrink-0 border border-white/10">
                        <Image
                          src={h.coverImageUrl}
                          alt={h.title}
                          fill
                          className="object-cover"
                        />
                      </div>
                    ) : (
                      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-amber-600 to-indigo-600 flex items-center justify-center font-bold text-white text-xs flex-shrink-0">
                        {h.title[0]}
                      </div>
                    )}

                    <div className="min-w-0">
                      <div className="text-sm font-semibold truncate group-hover:text-accent">
                        {h.title}
                      </div>
                      <div className="text-xs text-text-muted truncate flex items-center gap-1.5 mt-0.5 font-mono">
                        <span>{h.organizerName}</span>
                        <span>•</span>
                        <span>{h.mode === 'OFFLINE' ? `📍 ${h.indiaRegion || 'In-Person'}` : '🌐 Online'}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 flex-shrink-0">
                    {h.prizePool && Number(h.prizePool) > 0 ? (
                      <span className="px-2 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs font-mono">
                        ${Number(h.prizePool) >= 1000 ? `${(Number(h.prizePool)/1000).toFixed(0)}K` : h.prizePool}
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono">
                        Free
                      </span>
                    )}
                    <CornerDownLeft className="w-3.5 h-3.5 text-text-muted" />
                  </div>
                </Link>
              )
            })}
          </div>

          <div className="p-2.5 bg-black/40 text-center">
            <button
              onClick={() => {
                pushQuery(value)
                setIsOpen(false)
              }}
              className="text-xs font-mono text-accent hover:underline flex items-center justify-center gap-1.5 w-full"
            >
              <span>See all results for &ldquo;{value}&rdquo;</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
