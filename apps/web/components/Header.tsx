'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Bookmark, CalendarDays, ChevronDown, LogIn, LogOut, Plus, Shield } from 'lucide-react'
import { createSupabaseBrowserClient } from '@/lib/supabase/client'

type SessionUser = Awaited<ReturnType<ReturnType<typeof createSupabaseBrowserClient>['auth']['getUser']>>['data']['user']

export function Header() {
  const router = useRouter()
  const [user, setUser] = useState<SessionUser | null>(null)
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    const supabase = createSupabaseBrowserClient()

    const syncUser = async () => {
      const { data } = await supabase.auth.getUser()
      setUser(data.user ?? null)
    }

    syncUser()
    const { data: listener } = supabase.auth.onAuthStateChange(() => {
      syncUser()
    })

    return () => listener.subscription.unsubscribe()
  }, [])

  const isAdmin = Boolean(user?.email?.endsWith('@1ph.dev'))

  return (
    <header className="sticky top-0 z-50 bg-bg/95 backdrop-blur-sm border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14">
          <div className="flex items-center gap-6">
            <Link href="/" className="font-serif text-2xl text-text-primary hover:text-accent transition-colors duration-150">
              1ph
            </Link>
          </div>

          <div className="flex items-center gap-3">
            {user && (
              <Link
                href="/calendar"
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-chip border border-border text-text-muted text-sm font-mono hover:border-accent hover:text-accent transition-all duration-300"
                aria-label="Registered Hackathons Calendar"
              >
                <CalendarDays className="h-4 w-4" />
                <span className="hidden sm:inline">Calendar</span>
              </Link>
            )}
            <Link
              href="/submit"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-chip border border-border text-text-muted text-sm font-mono hover:border-accent hover:text-accent transition-all duration-300"
            >
              <Plus className="h-4 w-4 text-accent" />
              Submit
            </Link>

            {user ? (
              <div className="relative">
                <button
                  onClick={() => setMenuOpen((value) => !value)}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-chip border border-border text-text-muted text-sm font-mono hover:border-accent transition-all duration-150"
                >
                  {user.user_metadata?.avatar_url && (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={user.user_metadata.avatar_url} alt="avatar" className="w-5 h-5 rounded-full" />
                  )}
                  <span className="hidden sm:block max-w-[100px] truncate">
                    {user.user_metadata?.full_name?.split(' ')[0] ?? user.email?.split('@')[0] ?? 'You'}
                  </span>
                  <ChevronDown className="h-3 w-3" />
                </button>

                {menuOpen && (
                  <>
                    <div className="fixed inset-0 z-40" onClick={() => setMenuOpen(false)} />
                    <div className="absolute right-0 top-full mt-1 w-44 bg-card border border-border rounded-card shadow-lg overflow-hidden z-50 animate-fade-in">
                      <Link
                        href="/bookmarks"
                        className="block px-4 py-2.5 text-sm font-mono text-text-muted hover:text-text-primary hover:bg-tag-bg transition-colors"
                        onClick={() => setMenuOpen(false)}
                      >
                        <span className="inline-flex items-center gap-2"><Bookmark className="h-3.5 w-3.5" />Bookmarks</span>
                      </Link>
                      {isAdmin && (
                        <Link
                          href="/admin"
                          className="block px-4 py-2.5 text-sm font-mono text-text-muted hover:text-text-primary hover:bg-tag-bg transition-colors border-t border-border"
                          onClick={() => setMenuOpen(false)}
                        >
                          <span className="inline-flex items-center gap-2"><Shield className="h-3.5 w-3.5" />Admin</span>
                        </Link>
                      )}
                      <button
                        onClick={async () => {
                          await createSupabaseBrowserClient().auth.signOut()
                          setMenuOpen(false)
                          router.refresh()
                        }}
                        className="w-full text-left px-4 py-2.5 text-sm font-mono text-text-muted hover:text-text-primary hover:bg-tag-bg transition-colors border-t border-border"
                      >
                        <span className="inline-flex items-center gap-2"><LogOut className="h-3.5 w-3.5" />Sign out</span>
                      </button>
                    </div>
                  </>
                )}
              </div>
            ) : (
              <Link
                href="/login"
                className="inline-flex items-center gap-2 px-3 py-1.5 rounded-chip border border-border text-text-muted text-sm font-mono hover:border-accent hover:text-accent transition-all duration-150"
              >
                <LogIn className="h-4 w-4" />
                Login
              </Link>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
