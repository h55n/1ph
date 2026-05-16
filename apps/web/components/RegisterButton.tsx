'use client'

import { useState } from 'react'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { cn } from '@/lib/utils'

export function RegisterButton({ hackathonId, initialRegistered = false }: { hackathonId: string; initialRegistered?: boolean }) {
  const { data: session } = useSession()
  const router = useRouter()
  const [registered, setRegistered] = useState(initialRegistered)
  const [loading, setLoading] = useState(false)

  async function toggle(e: React.MouseEvent) {
    e.preventDefault()
    e.stopPropagation()
    if (!session) { 
      router.push(`/login?callbackUrl=${encodeURIComponent(window.location.pathname)}`)
      return 
    }
    setLoading(true)
    const prev = registered
    setRegistered(!prev)
    try {
      if (prev) {
        const res = await fetch(`/api/registrations/${hackathonId}`, { method: 'DELETE' })
        if (!res.ok) setRegistered(prev)
      } else {
        const res = await fetch('/api/registrations', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ hackathonId }),
        })
        if (!res.ok) setRegistered(prev)
      }
    } catch {
      setRegistered(prev)
    } finally {
      setLoading(false)
    }
  }

  return (
    <button
      onClick={toggle}
      disabled={loading}
      aria-label={registered ? 'Mark as unregistered' : 'Mark as registered'}
      className={cn(
        'flex items-center justify-center w-9 h-9 rounded-card border transition-all duration-150 text-sm',
        registered ? 'border-accent bg-accent/10 text-accent' : 'border-border text-text-muted hover:border-accent/50 hover:text-text-primary',
        loading && 'opacity-50 cursor-not-allowed'
      )}
    >
      {registered ? '🗓' : '📅'}
    </button>
  )
}
