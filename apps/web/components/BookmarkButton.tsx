'use client'

import { useState } from 'react'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { cn } from '@/lib/utils'

export function BookmarkButton({ hackathonId, initialBookmarked = false }: { hackathonId: string; initialBookmarked?: boolean }) {
  const { data: session } = useSession()
  const router = useRouter()
  const [bookmarked, setBookmarked] = useState(initialBookmarked)
  const [loading, setLoading] = useState(false)

  async function toggle(e: React.MouseEvent) {
    e.preventDefault()
    e.stopPropagation()
    if (!session) { 
      router.push(`/login?callbackUrl=${encodeURIComponent(window.location.pathname)}`)
      return 
    }
    setLoading(true)
    const prev = bookmarked
    setBookmarked(!prev)
    try {
      if (prev) {
        const res = await fetch(`/api/bookmarks/${hackathonId}`, { method: 'DELETE' })
        if (!res.ok) setBookmarked(prev)
      } else {
        const res = await fetch('/api/bookmarks', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ hackathonId }),
        })
        if (!res.ok) setBookmarked(prev)
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
