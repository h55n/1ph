import type { Metadata } from 'next'
import './globals.css'
import { Header } from '@/components/Header'
import { Providers } from '@/components/Providers'

export const metadata: Metadata = {
  title: '1ph — Every hackathon. One place.',
  description:
    'The cleanest hackathon directory on the internet. Global + India hackathons, sorted by prestige, prize, and deadline. No clutter, no ads.',
  metadataBase: new URL('https://1ph.dev'),
  openGraph: {
    title: '1ph — Every hackathon. One place.',
    description:
      'Global + India hackathons in one clean directory. Filter by theme, prize, deadline, and more.',
    url: 'https://1ph.dev',
    siteName: '1ph',
    images: [{ url: '/og-default.png', width: 1200, height: 630 }],
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: '1ph — Every hackathon. One place.',
    description: 'Global + India hackathons in one clean directory.',
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-bg text-text-primary font-sans antialiased min-h-screen flex flex-col">
        <Providers>
          <Header />
          <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6 pb-16 w-full">
            {children}
          </main>
          <footer className="py-12 border-t border-border/50 text-center">
            <p className="text-[10px] font-mono text-text-muted tracking-widest uppercase opacity-50">
              Made with <span className="text-accent">❤</span> by hssn
            </p>
          </footer>
        </Providers>
      </body>
    </html>
  )
}
