'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { cn } from '@/lib/utils'
import { CalendarCheck, CalendarPlus } from 'lucide-react'

export function RegisterButton({ 
  hackathonId, 
  initialRegistered = false,
  className 
}: { 
  hackathonId: string
  initialRegistered?: boolean
  className?: string 
}) {
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
        'flex items-center justify-center w-8 h-8 rounded-full border transition-all duration-200',
        registered 
          ? 'border-emerald-500/80 bg-emerald-500/25 text-emerald-400 shadow-sm shadow-emerald-500/20' 
          : 'border-white/20 bg-black/40 backdrop-blur-md text-white/70 hover:border-white/40 hover:text-white hover:bg-black/70 shadow-sm',
        loading && 'opacity-50 cursor-not-allowed',
        className
      )}
    >
      {registered ? (
        <CalendarCheck className="w-3.5 h-3.5 text-emerald-400" />
      ) : (
        <CalendarPlus className="w-3.5 h-3.5" />
      )}
    </button>
  )
}
