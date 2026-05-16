'use client'

import { signIn } from 'next-auth/react'
import { useSearchParams, useRouter } from 'next/navigation'
import { Suspense, useState } from 'react'

function LoginContent() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const callbackUrl = searchParams.get('callbackUrl') ?? '/'
  
  const [isRegistering, setIsRegistering] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    if (isRegistering) {
      try {
        const res = await fetch('/api/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password, name })
        })

        if (!res.ok) {
          let errorMsg = 'Failed to register'
          try {
            const data = await res.json()
            errorMsg = data.error || errorMsg
          } catch {
            // response was not JSON
          }
          throw new Error(errorMsg)
        }

        // Successfully registered, now sign in
        const result = await signIn('credentials', {
          redirect: false,
          email,
          password,
        })

        if (result?.error) {
          setError('Invalid email or password')
        } else {
          router.push(callbackUrl)
          router.refresh()
        }
      } catch (err: any) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    } else {
      try {
        const result = await signIn('credentials', {
          redirect: false,
          email,
          password,
        })

        if (result?.error) {
          setError('Invalid email or password')
        } else {
          router.push(callbackUrl)
          router.refresh()
        }
      } catch (err: any) {
        setError('Something went wrong')
      } finally {
        setLoading(false)
      }
    }
  }

  return (
    <div className="max-w-sm mx-auto pt-20 space-y-6">
      <div className="text-center">
        <h1 className="font-serif text-3xl text-text-primary mb-2">
          {isRegistering ? 'Create Account' : 'Welcome back.'}
        </h1>
        <p className="font-mono text-sm text-text-muted">
          {isRegistering ? 'Sign up to save hackathons.' : 'Sign in to save hackathons.'}
        </p>
      </div>

      <div className="bg-card border border-border rounded-card p-6 space-y-4">
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="p-3 text-sm text-red-500 bg-red-500/10 border border-red-500/20 rounded-md">
              {error}
            </div>
          )}

          {isRegistering && (
            <div>
              <label className="block font-mono text-xs text-text-muted mb-1">Name</label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm text-text-primary focus:border-accent focus:outline-none"
                placeholder="Ada Lovelace"
              />
            </div>
          )}

          <div>
            <label className="block font-mono text-xs text-text-muted mb-1">Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm text-text-primary focus:border-accent focus:outline-none"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label className="block font-mono text-xs text-text-muted mb-1">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm text-text-primary focus:border-accent focus:outline-none"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-accent text-background font-mono text-sm font-bold py-2.5 rounded-md hover:bg-accent/90 transition-colors disabled:opacity-50"
          >
            {loading ? 'Please wait...' : (isRegistering ? 'Sign Up' : 'Sign In')}
          </button>
        </form>

        <div className="relative py-4">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-border"></div>
          </div>
          <div className="relative flex justify-center text-xs">
            <span className="bg-card px-2 text-text-muted font-mono">Or continue with</span>
          </div>
        </div>

        <div className="space-y-3">
          <button
            onClick={() => signIn('google', { callbackUrl })}
            className="w-full flex items-center justify-center gap-3 py-2.5 rounded-card border border-border text-text-primary font-mono text-sm hover:border-accent hover:bg-tag-bg transition-all duration-150"
          >
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.875 2.684-6.615z" fill="#4285F4"/>
              <path d="M9 18c2.43 0 4.467-.806 5.956-2.184l-2.908-2.258c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 0 0 9 18z" fill="#34A853"/>
              <path d="M3.964 10.707A5.41 5.41 0 0 1 3.682 9c0-.593.102-1.17.282-1.707V4.961H.957A8.996 8.996 0 0 0 0 9c0 1.452.348 2.827.957 4.039l3.007-2.332z" fill="#FBBC05"/>
              <path d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 0 0 .957 4.96L3.964 7.292C4.672 5.165 6.656 3.58 9 3.58z" fill="#EA4335"/>
            </svg>
            Google
          </button>

          <button
            onClick={() => signIn('github', { callbackUrl })}
            className="w-full flex items-center justify-center gap-3 py-2.5 rounded-card border border-border text-text-primary font-mono text-sm hover:border-accent hover:bg-tag-bg transition-all duration-150"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0 1 12 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/>
            </svg>
            GitHub
          </button>
        </div>
      </div>

      <p className="font-mono text-xs text-text-muted text-center">
        {isRegistering ? 'Already have an account?' : 'Don\'t have an account?'}
        {' '}
        <button 
          onClick={() => setIsRegistering(!isRegistering)}
          className="text-accent hover:underline"
        >
          {isRegistering ? 'Sign in' : 'Create one'}
        </button>
      </p>

      <p className="font-mono text-xs text-text-muted text-center pt-4">
        Browsing is always free. No login needed to find hackathons.
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
