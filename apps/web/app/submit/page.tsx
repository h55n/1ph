export default function SubmitPage() {
  const formUrl = process.env.NEXT_PUBLIC_ORGANIZER_FORM_URL ?? '#'

  return (
    <div className="max-w-xl mx-auto pt-12 space-y-8">
      <div>
        <h1 className="font-serif text-4xl text-text-primary mb-3">List your hackathon.</h1>
        <p className="font-sans text-text-muted text-sm leading-relaxed">
          1ph reviews every submission before it goes live. No spam, no noise —
          just hackathons worth a builder&apos;s time.
        </p>
      </div>

      <div className="bg-card border border-border rounded-card p-6 space-y-4">
        <h2 className="font-mono text-sm text-text-muted uppercase tracking-wider">How it works</h2>
        <ol className="space-y-3">
          {[
            'Fill out the form below — takes 3 minutes.',
            'We review your submission within 48 hours.',
            'Approved hackathons go live with a verified badge.',
          ].map((step, i) => (
            <li key={i} className="flex items-start gap-3">
              <span className="flex-shrink-0 w-5 h-5 rounded-full bg-tag-bg border border-border flex items-center justify-center font-mono text-xs text-accent">
                {i + 1}
              </span>
              <span className="font-sans text-sm text-text-muted">{step}</span>
            </li>
          ))}
        </ol>
      </div>

      <a
        href={formUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="block w-full py-3 rounded-card bg-accent text-bg font-mono font-medium text-center text-sm hover:bg-accent/90 transition-colors duration-150"
      >
        Submit via Google Form →
      </a>

      <p className="font-mono text-xs text-text-muted text-center">
        Questions? Email{' '}
        <a href="mailto:hello@1ph.dev" className="text-accent hover:underline">hello@1ph.dev</a>
      </p>
    </div>
  )
}
