import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
      <h1 className="font-serif text-6xl text-text-primary mb-4">404</h1>
      <p className="font-mono text-text-muted mb-8">
        This hackathon doesn&apos;t exist — or it&apos;s been removed.
      </p>
      <Link
        href="/"
        className="px-6 py-2.5 bg-accent text-bg font-mono text-sm rounded-card hover:bg-accent/90 transition-colors"
      >
        Browse all hackathons →
      </Link>
    </div>
  )
}
