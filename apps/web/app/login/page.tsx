'use client'

import { Suspense, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { motion } from 'framer-motion'
import { ArrowRight, Mail, Sparkles } from 'lucide-react'
import { createSupabaseBrowserClient } from '@/lib/supabase/client'
import { cn } from '@/lib/utils'

function LoginContent() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const callbackUrl = searchParams.get('callbackUrl') ?? '/'

  const [activeTab, setActiveTab] = useState<'login' | 'signup'>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const supabase = createSupabaseBrowserClient()

  const handlePasswordFlow = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    const payload = activeTab === 'signup'
      ? { email, password, options: { data: { full_name: name } } }
      : { email, password }

    const { error: authError } = activeTab === 'signup'
      ? await supabase.auth.signUp(payload)
      : await supabase.auth.signInWithPassword(payload)

    if (authError) {
      setError(authError.message)
    } else if (activeTab === 'signup') {
      setError('Check your inbox to finish creating your account.')
    } else {
      router.push(callbackUrl)
      router.refresh()
    }

    setLoading(false)
  }

  const signInWithProvider = async (provider: 'google' | 'github') => {
    setLoading(true)
    setError(null)
    const { error: authError } = await supabase.auth.signInWithOAuth({
      provider,
      options: { redirectTo: `${window.location.origin}${callbackUrl}` },
    })
    if (authError) setError(authError.message)
    setLoading(false)
  }

  return (
    <div className="max-w-sm mx-auto pt-20 space-y-6">
      <div className="text-center mb-8">
        <h1 className="font-serif text-3xl text-text-primary mb-2">
          {activeTab === 'signup' ? 'Create account' : 'Welcome back'}
        </h1>
        <p className="font-mono text-sm text-text-muted">
          {activeTab === 'signup' ? 'Sign up to save hackathons.' : 'Sign in to save hackathons.'}
        </p>
      </div>

      <div className="flex bg-card border border-border p-1 rounded-card mb-4 relative">
        <button
          onClick={() => { setActiveTab('login'); setError(null) }}
          className={cn('flex-1 relative z-10 py-2 text-sm font-mono transition-colors duration-300', activeTab === 'login' ? 'text-text-primary' : 'text-text-muted hover:text-text-primary')}
        >
          {activeTab === 'login' && <motion.div layoutId="login-tab-pill" className="absolute inset-0 bg-tag-bg border border-border rounded-md z-[-1]" transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }} />}
          Sign In
        </button>
        <button
          onClick={() => { setActiveTab('signup'); setError(null) }}
          className={cn('flex-1 relative z-10 py-2 text-sm font-mono transition-colors duration-300', activeTab === 'signup' ? 'text-text-primary' : 'text-text-muted hover:text-text-primary')}
        >
          {activeTab === 'signup' && <motion.div layoutId="login-tab-pill" className="absolute inset-0 bg-tag-bg border border-border rounded-md z-[-1]" transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }} />}
          Sign Up
        </button>
      </div>

      <div className="bg-card border border-border rounded-card p-6 space-y-4">
        <form onSubmit={handlePasswordFlow} className="space-y-4">
          {error && <div className={cn('p-3 text-sm border rounded-md animate-fade-in', error.includes('inbox') ? 'text-accent bg-accent/10 border-accent/20' : 'text-red-500 bg-red-500/10 border-red-500/20')}>{error}</div>}

          {activeTab === 'signup' && (
            <div className="animate-fade-in">
              <label className="block font-mono text-xs text-text-muted mb-1">Name</label>
              <input value={name} onChange={(e) => setName(e.target.value)} required className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm text-text-primary focus:border-accent focus:outline-none transition-colors" placeholder="Ada Lovelace" />
            </div>
          )}

          <div>
            <label className="block font-mono text-xs text-text-muted mb-1">Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm text-text-primary focus:border-accent focus:outline-none transition-colors" placeholder="you@example.com" />
          </div>

          <div>
            <label className="block font-mono text-xs text-text-muted mb-1">Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm text-text-primary focus:border-accent focus:outline-none transition-colors" placeholder="••••••••" />
          </div>

          <button type="submit" disabled={loading} className="w-full bg-accent text-background font-mono text-sm font-bold py-2.5 rounded-md hover:bg-accent/90 transition-all active:scale-95 disabled:opacity-50 inline-flex items-center justify-center gap-2">
            {loading ? 'Please wait...' : activeTab === 'signup' ? 'Create account' : 'Sign in'}
            <ArrowRight className="h-4 w-4" />
          </button>
        </form>

        <div className="relative py-4">
          <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-border" /></div>
          <div className="relative flex justify-center text-xs">
            <span className="bg-card px-2 text-text-muted font-mono">Or continue with</span>
          </div>
        </div>

        <div className="space-y-3">
          <button onClick={() => signInWithProvider('google')} className="w-full flex items-center justify-center gap-3 py-2.5 rounded-card border border-border text-text-primary font-mono text-sm hover:border-accent hover:bg-tag-bg transition-all duration-150">
            <Mail className="h-4 w-4" />
            Google
          </button>
          <button onClick={() => signInWithProvider('github')} className="w-full flex items-center justify-center gap-3 py-2.5 rounded-card border border-border text-text-primary font-mono text-sm hover:border-accent hover:bg-tag-bg transition-all duration-150">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <path d="M12 0C5.372 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.6.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.5 11.5 0 0 1 12 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z" />
            </svg>
            GitHub
          </button>
        </div>
      </div>

      <p className="font-mono text-xs text-text-muted text-center pt-4 inline-flex items-center justify-center gap-2">
        <Sparkles className="h-3.5 w-3.5" /> Browsing is always free. No login needed to find hackathons.
      </p>
    </div>
  )
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="pt-20 text-center font-mono text-text-muted text-sm">Loading...</div>}>
      <LoginContent />
    </Suspense>
  )
}
