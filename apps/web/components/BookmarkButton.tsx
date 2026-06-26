'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { cn } from '@/lib/utils'

export function BookmarkButton({ hackathonId, initialBookmarked = false }: { hackathonId: string; initialBookmarked?: boolean }) {
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
        'flex items-center justify-center w-9 h-9 rounded-card border transition-all duration-150',
        bookmarked ? 'border-accent bg-accent/10 text-accent' : 'border-border text-text-muted hover:border-accent/50 hover:text-text-primary',
        loading && 'opacity-50 cursor-not-allowed'
      )}
    >
      {bookmarked ? '★' : '☆'}
    </button>
  )
}
