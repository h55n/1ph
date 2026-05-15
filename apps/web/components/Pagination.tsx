'use client'

import { useRouter, useSearchParams, usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'

export function Pagination({ totalItems, pageSize }: { totalItems: number; pageSize: number }) {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()
  
  const parsedPage = parseInt(searchParams.get('page') ?? '1', 10)
  const currentPage = isNaN(parsedPage) ? 1 : Math.max(1, parsedPage)
  const totalPages = Math.ceil(totalItems / pageSize)

  if (totalPages <= 1) return null

  function setPage(page: number) {
    const params = new URLSearchParams(searchParams.toString())
    params.set('page', page.toString())
    router.push(`${pathname}?${params.toString()}`)
  }

  return (
    <div className="flex items-center justify-center gap-4 pt-10 pb-20">
      <button
        onClick={() => setPage(currentPage - 1)}
        disabled={currentPage === 1}
        className={cn(
          "px-4 py-2 font-mono text-sm rounded-md border transition-all",
          currentPage === 1 
            ? "border-border text-border cursor-not-allowed opacity-50" 
            : "border-border text-text-primary hover:border-accent hover:text-accent bg-card"
        )}
      >
        ← Previous
      </button>
      
      <span className="font-mono text-sm text-text-muted">
        Page {currentPage} of {totalPages}
      </span>

      <button
        onClick={() => setPage(currentPage + 1)}
        disabled={currentPage === totalPages}
        className={cn(
          "px-4 py-2 font-mono text-sm rounded-md border transition-all",
          currentPage === totalPages 
            ? "border-border text-border cursor-not-allowed opacity-50" 
            : "border-border text-text-primary hover:border-accent hover:text-accent bg-card"
        )}
      >
        Next →
      </button>
    </div>
  )
}
