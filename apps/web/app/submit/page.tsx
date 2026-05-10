export default function SubmitPage() {
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
        <form action="https://formsubmit.co/hassan0rehman@gmail.com" method="POST" className="space-y-4">
          {/* FormSubmit configurations */}
          <input type="hidden" name="_subject" value="New Hackathon Submission - 1ph" />
          <input type="hidden" name="_captcha" value="false" />
          <input type="hidden" name="_next" value="https://1ph.vercel.app/" />

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
            className="w-full py-3 mt-4 rounded-card bg-accent text-bg font-mono font-medium text-center text-sm hover:bg-accent/90 transition-colors duration-150"
          >
            Submit Hackathon →
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
