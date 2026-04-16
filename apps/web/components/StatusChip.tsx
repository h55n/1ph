import { cn } from '@/lib/utils'

type Status = 'UPCOMING' | 'OPEN' | 'CLOSING_SOON' | 'CLOSED'

const CONFIG: Record<Status, { label: string; dotColor: string; textColor: string; pulse: boolean }> = {
  OPEN:         { label: 'Open',         dotColor: 'bg-open',    textColor: 'text-open',    pulse: false },
  CLOSING_SOON: { label: 'Closing Soon', dotColor: 'bg-closing', textColor: 'text-closing', pulse: true },
  UPCOMING:     { label: 'Upcoming',     dotColor: 'bg-upcoming',textColor: 'text-upcoming',pulse: false },
  CLOSED:       { label: 'Closed',       dotColor: 'bg-closed',  textColor: 'text-text-muted', pulse: false },
}

interface StatusChipProps {
  status: Status
  className?: string
}

export function StatusChip({ status, className }: StatusChipProps) {
  const { label, dotColor, textColor, pulse } = CONFIG[status]

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 text-xs font-mono font-medium',
        textColor,
        className
      )}
      role="status"
      aria-label={`Status: ${label}`}
    >
      <span
        className={cn(
          'w-1.5 h-1.5 rounded-full flex-shrink-0',
          dotColor,
          pulse && 'animate-pulse-dot'
        )}
      />
      {label}
    </span>
  )
}
