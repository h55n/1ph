import { Suspense } from 'react'
import LoginContent from './LoginContent'

export const dynamic = 'force-dynamic'

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="pt-20 text-center font-mono text-text-muted text-sm">Loading...</div>}>
      <LoginContent />
    </Suspense>
  )
}
