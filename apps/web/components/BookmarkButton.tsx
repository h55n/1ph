'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { cn } from '@/lib/utils'
import { Bookmark } from 'lucide-react'

export function BookmarkButton({ 
  hackathonId, 
  initialBookmarked = false,
  className 
}: { 
  hackathonId: string
  initialBookmarked?: boolean
  className?: string 
}) {
  const router = useRouter()
  const [bookmarked, setBookmarked] = useState(initialBookmarked)
  const [loading, setLoading] = useState(false)

  async function toggle(e: React.MouseEvent) {
    e.preventDefault()
    e.stopPropagation()
    setLoading(true)
    const prev = bookmarked
    setBookmarked(!prev)
    try {
      const res = await fetch(prev ? `/api/bookmarks/${hackathonId}` : '/api/bookmarks', {
        method: prev ? 'DELETE' : 'POST',
        headers: prev ? undefined : { 'Content-Type': 'application/json' },
        body: prev ? undefined : JSON.stringify({ hackathonId }),
      })
      if (res.status === 401) {
        router.push(`/login?callbackUrl=${encodeURIComponent(window.location.pathname)}`)
        setBookmarked(prev)
      } else if (!res.ok) {
        setBookmarked(prev)
      }
    } catch {
      setBookmarked(prev)
    } finally {
      setLoading(false)
    }
  }

  return (
    <button
      onClick={toggle}
      disabled={loading}
      aria-label={bookmarked ? 'Remove bookmark' : 'Save hackathon'}
      className={cn(
        'flex items-center justify-center w-8 h-8 rounded-full border transition-all duration-200',
        bookmarked 
          ? 'border-accent/80 bg-accent/25 text-accent shadow-sm shadow-accent/20' 
          : 'border-white/20 bg-black/40 backdrop-blur-md text-white/70 hover:border-white/40 hover:text-white hover:bg-black/70 shadow-sm',
        loading && 'opacity-50 cursor-not-allowed',
        className
      )}
    >
      <Bookmark className={cn('w-3.5 h-3.5 transition-transform duration-200 active:scale-90', bookmarked && 'fill-current')} />
    </button>
  )
}
