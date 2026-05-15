'use client'

import { useState } from 'react'
import { submitHackathon } from './actions'

export default function SubmitPage() {
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    const formData = new FormData(e.currentTarget)
    
    try {
      const res = await submitHackathon(formData)
      if (res?.error) {
        setError(res.error)
      } else {
        setSuccess(true)
      }
    } catch (err) {
      setError('An unexpected error occurred.')
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className="max-w-xl mx-auto pt-20 text-center space-y-4">
        <div className="w-16 h-16 bg-accent/20 rounded-full flex items-center justify-center mx-auto mb-6">
          <span className="text-2xl">🎉</span>
        </div>
        <h1 className="font-serif text-4xl text-text-primary">Submission Received!</h1>
        <p className="font-sans text-text-muted text-sm leading-relaxed">
          Thanks for adding to 1ph. Our team will review your hackathon shortly.
        </p>
        <div className="pt-8">
          <a href="/" className="px-6 py-2 bg-accent text-background rounded-card font-mono text-sm hover:bg-accent/90 transition-colors">
            Back to Home
          </a>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-xl mx-auto pt-12 space-y-8">
      <div>
        <h1 className="font-serif text-4xl text-text-primary mb-3">List your hackathon.</h1>
        <p className="font-sans text-text-muted text-sm leading-relaxed">
          1ph reviews every submission before it goes live. No spam, no noise —
          just hackathons worth a builder&apos;s time.
        </p>
      </div>

      <div className="bg-card border border-border rounded-card p-6">
        {error && (
          <div className="mb-4 p-3 rounded bg-red-500/10 border border-red-500/20 text-red-500 text-sm">
            {error}
          </div>
        )}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block font-mono text-xs text-text-muted mb-1" htmlFor="orgName">Organizer Name *</label>
            <input required type="text" id="orgName" name="Organizer Name" placeholder="e.g. MLH" className="w-full bg-bg border border-border rounded-chip px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent" />
          </div>

          <div>
            <label className="block font-mono text-xs text-text-muted mb-1" htmlFor="title">Hackathon Title *</label>
            <input required type="text" id="title" name="Hackathon Title" placeholder="e.g. HackMIT 2026" className="w-full bg-bg border border-border rounded-chip px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent" />
          </div>

          <div>
            <label className="block font-mono text-xs text-text-muted mb-1" htmlFor="applyUrl">Apply URL *</label>
            <input required type="url" id="applyUrl" name="Apply URL" placeholder="https://..." className="w-full bg-bg border border-border rounded-chip px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent" />
          </div>

          <div>
            <label className="block font-mono text-xs text-text-muted mb-1" htmlFor="email">Your Email *</label>
            <input required type="email" id="email" name="Email" placeholder="To reach you if we have questions" className="w-full bg-bg border border-border rounded-chip px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent" />
          </div>

          <div>
            <label className="block font-mono text-xs text-text-muted mb-1" htmlFor="notes">Additional Details (Optional)</label>
            <textarea id="notes" name="Additional Notes" rows={3} placeholder="Prizes, mode, eligibility, etc." className="w-full bg-bg border border-border rounded-chip px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent"></textarea>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 mt-4 rounded-card bg-accent text-bg font-mono font-medium text-center text-sm hover:bg-accent/90 transition-colors duration-150 disabled:opacity-50"
          >
            {loading ? 'Submitting...' : 'Submit Hackathon →'}
          </button>
        </form>
      </div>

      <p className="font-mono text-xs text-text-muted text-center pb-8">
        Questions? Email{' '}
        <a href="mailto:hello@1ph.dev" className="text-accent hover:underline">hello@1ph.dev</a>
      </p>
    </div>
  )
}
