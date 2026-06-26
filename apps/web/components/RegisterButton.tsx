'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { cn } from '@/lib/utils'

export function RegisterButton({ hackathonId, initialRegistered = false }: { hackathonId: string; initialRegistered?: boolean }) {
  const router = useRouter()
  const [registered, setRegistered] = useState(initialRegistered)
  const [loading, setLoading] = useState(false)

  async function toggle(e: React.MouseEvent) {
    e.preventDefault()
    e.stopPropagation()
    setLoading(true)
    const prev = registered
    setRegistered(!prev)
    try {
      const res = await fetch(prev ? `/api/registrations/${hackathonId}` : '/api/registrations', {
        method: prev ? 'DELETE' : 'POST',
        headers: prev ? undefined : { 'Content-Type': 'application/json' },
        body: prev ? undefined : JSON.stringify({ hackathonId }),
      })
      if (res.status === 401) {
        router.push(`/login?callbackUrl=${encodeURIComponent(window.location.pathname)}`)
        setRegistered(prev)
      } else if (!res.ok) {
        setRegistered(prev)
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
