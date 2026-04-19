import type { Metadata } from 'next'
import { DM_Serif_Display, JetBrains_Mono, Inter } from 'next/font/google'
import './globals.css'
import { Header } from '@/components/Header'
import { Providers } from '@/components/Providers'

const dmSerifDisplay = DM_Serif_Display({
  subsets: ['latin'],
  weight: ['400'],
  variable: '--font-serif',
  display: 'swap',
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  weight: ['400', '500'],
  variable: '--font-mono',
  display: 'swap',
})

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-sans',
  display: 'swap',
})

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
    <html lang="en" className={`${dmSerifDisplay.variable} ${jetbrainsMono.variable} ${inter.variable}`}>
      <body className="bg-bg text-text-primary font-sans antialiased min-h-screen">
        <Providers>
          <Header />
          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6 pb-16">
            {children}
          </main>
        </Providers>
      </body>
    </html>
  )
}
