'use client'

import Link from 'next/link'
import { useSession, signIn, signOut } from 'next-auth/react'
import { useState } from 'react'

export function Header() {
  const { data: session, status } = useSession()
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <header className="sticky top-0 z-50 bg-bg/95 backdrop-blur-sm border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14">
          <Link href="/" className="font-serif text-2xl text-text-primary hover:text-accent transition-colors duration-150">
            1ph
          </Link>

          <div className="flex items-center gap-3">
            <Link
              href="/submit"
              className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-chip border border-border text-text-muted text-sm font-mono hover:border-accent hover:text-accent transition-all duration-150"
            >
              <span className="text-accent font-bold">+</span>
              Submit
            </Link>

            {status === 'loading' ? (
              <div className="w-20 h-7 bg-card rounded-chip animate-pulse" />
            ) : session ? (
              <div className="relative">
                <button
                  onClick={() => setMenuOpen(!menuOpen)}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-chip border border-border text-text-muted text-sm font-mono hover:border-accent transition-all duration-150"
                >
                  {session.user?.image && (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={session.user.image} alt="avatar" className="w-5 h-5 rounded-full" />
                  )}
                  <span className="hidden sm:block max-w-[100px] truncate">
                    {session.user?.name?.split(' ')[0]}
                  </span>
                  <span className="text-xs">▾</span>
                </button>

                {menuOpen && (
                  <div className="absolute right-0 top-full mt-1 w-40 bg-card border border-border rounded-card shadow-lg overflow-hidden">
                    <Link
                      href="/bookmarks"
                      className="block px-4 py-2.5 text-sm font-mono text-text-muted hover:text-text-primary hover:bg-tag-bg transition-colors"
                      onClick={() => setMenuOpen(false)}
                    >
                      Bookmarks
                    </Link>
                    {(session.user as { role?: string })?.role === 'ADMIN' && (
                      <Link
                        href="/admin"
                        className="block px-4 py-2.5 text-sm font-mono text-text-muted hover:text-text-primary hover:bg-tag-bg transition-colors border-t border-border"
                        onClick={() => setMenuOpen(false)}
                      >
                        Admin
                      </Link>
                    )}
                    <button
                      onClick={() => { signOut(); setMenuOpen(false) }}
                      className="w-full text-left px-4 py-2.5 text-sm font-mono text-text-muted hover:text-text-primary hover:bg-tag-bg transition-colors border-t border-border"
                    >
                      Sign out
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <button
                onClick={() => signIn()}
                className="px-3 py-1.5 rounded-chip border border-border text-text-muted text-sm font-mono hover:border-accent hover:text-accent transition-all duration-150"
              >
                Login
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
