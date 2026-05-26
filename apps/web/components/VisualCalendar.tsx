'use client'

import { useState } from 'react'
import {
  format,
  addMonths,
  subMonths,
  startOfMonth,
  endOfMonth,
  startOfWeek,
  endOfWeek,
  isSameMonth,
  isSameDay,
  addDays,
  startOfDay,
} from 'date-fns'
import { ChevronLeft, ChevronRight, X, ExternalLink, MapPin, Trophy, Calendar as CalendarIcon } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { formatPrize } from '@/lib/formatters'
import Link from 'next/link'
import { StatusChip } from './StatusChip'

interface EventData {
  id: string
  slug: string
  title: string
  organizerName: string
  status: any
  prizePool?: number | null
  prizeCurrency?: string | null
  prizeDescription?: string | null
  eventStart: Date | string | null
  eventEnd?: Date | string | null
  registrationClose: Date | string | null
  applyUrl?: string
  mode: string
  indiaRegion?: string | null
}

export function VisualCalendar({ events }: { events: EventData[] }) {
  const [currentMonth, setCurrentMonth] = useState(() => {
    if (!events.length) return new Date()
    // Find the first event that ends after today (upcoming)
    const now = new Date()
    const upcoming = events.filter(e => {
      const end = e.eventEnd ? new Date(e.eventEnd) : new Date((e.eventStart || e.registrationClose) as string | Date)
      return end >= now
    })
    
    // Sort upcoming events by start date
    upcoming.sort((a, b) => {
      const startA = new Date((a.eventStart || a.registrationClose) as string | Date).getTime()
      const startB = new Date((b.eventStart || b.registrationClose) as string | Date).getTime()
      return startA - startB
    })

    if (upcoming.length > 0) {
      return new Date((upcoming[0].eventStart || upcoming[0].registrationClose) as string | Date)
    }
    // Fallback to the latest event if all are past
    const latest = events.reduce((a, b) => {
      const startA = new Date((a.eventStart || a.registrationClose) as string | Date).getTime()
      const startB = new Date((b.eventStart || b.registrationClose) as string | Date).getTime()
      return startA > startB ? a : b
    })
    return new Date((latest.eventStart || latest.registrationClose) as string | Date)
  })
  
  const [selectedEvent, setSelectedEvent] = useState<EventData | null>(null)

  const renderHeader = () => {
    return (
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-serif text-text-primary">
          {format(currentMonth, 'MMMM yyyy')}
        </h2>
        <div className="flex gap-2">
          <button
            onClick={() => setCurrentMonth(subMonths(currentMonth, 1))}
            className="p-2 border border-border rounded-chip hover:bg-tag-bg transition-colors"
          >
            <ChevronLeft size={18} />
          </button>
          <button
            onClick={() => setCurrentMonth(addMonths(currentMonth, 1))}
            className="p-2 border border-border rounded-chip hover:bg-tag-bg transition-colors"
          >
            <ChevronRight size={18} />
          </button>
        </div>
      </div>
    )
  }

  const renderDays = () => {
    const days = []
    const startDate = startOfWeek(currentMonth)
    for (let i = 0; i < 7; i++) {
      days.push(
        <div key={i} className="text-center font-mono text-xs text-text-muted py-2">
          {format(addDays(startDate, i), 'EEE')}
        </div>
      )
    }
    return <div className="grid grid-cols-7 mb-2">{days}</div>
  }

  const renderCells = () => {
    const monthStart = startOfMonth(currentMonth)
    const monthEnd = endOfMonth(monthStart)
    const startDate = startOfWeek(monthStart)
    const endDate = endOfWeek(monthEnd)

    const rows = []
    let days = []
    let day = startDate
    let formattedDate = ''

    while (day <= endDate) {
      for (let i = 0; i < 7; i++) {
        formattedDate = format(day, 'd')
        const cloneDay = day
        
        // Find events that span across this day
        const dayEvents = events.filter(e => {
          if (!e.eventStart && !e.registrationClose) return false
          const start = startOfDay(new Date((e.eventStart || e.registrationClose) as string | Date))
          const end = e.eventEnd ? startOfDay(new Date(e.eventEnd)) : start
          const current = startOfDay(cloneDay)
          return current >= start && current <= end
        })

        const isCurrentMonth = isSameMonth(day, monthStart)
        const isToday = isSameDay(day, new Date())

        days.push(
          <div
            key={day.toISOString()}
            className={`min-h-[100px] sm:min-h-[120px] p-1 sm:p-2 border border-border/50 bg-card/20 transition-colors
              ${!isCurrentMonth ? 'opacity-30' : ''}
              ${isToday ? 'bg-accent/5' : ''}
            `}
          >
            <div className="flex justify-end mb-1">
              <span className={`text-xs font-mono w-6 h-6 flex items-center justify-center rounded-full
                ${isToday ? 'bg-accent text-background font-bold' : 'text-text-muted'}
              `}>
                {formattedDate}
              </span>
            </div>
            <div className="flex flex-col gap-1 overflow-y-auto max-h-[80px] no-scrollbar">
              {dayEvents.map(evt => (
                <button
                  key={evt.id}
                  onClick={() => setSelectedEvent(evt)}
                  className="w-full text-left px-1.5 py-1 text-[10px] sm:text-xs rounded bg-accent/10 border border-accent/20 text-accent truncate hover:bg-accent/20 transition-colors"
                >
                  {evt.title}
                </button>
              ))}
            </div>
          </div>
        )
        day = addDays(day, 1)
      }
      rows.push(
        <div className="grid grid-cols-7" key={day.toISOString()}>
          {days}
        </div>
      )
      days = []
    }
    return <div className="border border-border/50 rounded-lg overflow-hidden bg-background">{rows}</div>
  }

  return (
    <div>
      {renderHeader()}
      {renderDays()}
      {renderCells()}

      <AnimatePresence>
        {selectedEvent && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedEvent(null)}
              className="absolute inset-0 bg-background/80 backdrop-blur-sm"
            />
            <motion.div
              initial={{ scale: 0.95, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.95, opacity: 0, y: 20 }}
              className="relative w-full max-w-lg bg-card border border-border rounded-card shadow-2xl p-6 z-10"
            >
              <button
                onClick={() => setSelectedEvent(null)}
                className="absolute top-4 right-4 text-text-muted hover:text-text-primary transition-colors"
              >
                <X size={20} />
              </button>

              <div className="mb-4">
                <p className="text-xs font-mono text-text-muted mb-2">{selectedEvent.organizerName}</p>
                <h3 className="text-2xl font-serif text-text-primary leading-tight mb-3">
                  {selectedEvent.title}
                </h3>
                <StatusChip status={selectedEvent.status} />
              </div>

              <div className="space-y-4 mb-6">
                <div className="flex items-center gap-3 text-sm font-mono text-text-muted">
                  <CalendarIcon size={16} className="text-accent" />
                  <span>
                    {format(new Date((selectedEvent.eventStart || selectedEvent.registrationClose) as string | Date), 'MMMM d, yyyy')}
                  </span>
                </div>
                
                <div className="flex items-center gap-3 text-sm font-mono text-text-muted">
                  <Trophy size={16} className="text-yellow-500" />
                  <span>
                    {selectedEvent.prizeDescription || formatPrize(selectedEvent.prizePool, selectedEvent.prizeCurrency)}
                  </span>
                </div>

                <div className="flex items-center gap-3 text-sm font-mono text-text-muted">
                  <MapPin size={16} className="text-blue-400" />
                  <span className="capitalize">
                    {selectedEvent.mode.toLowerCase()} {selectedEvent.indiaRegion ? `• ${selectedEvent.indiaRegion}` : ''}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-3 pt-4 border-t border-border">
                <Link
                  href={`/hackathon/${selectedEvent.slug}`}
                  className="flex-1 text-center bg-tag-bg text-text-primary border border-border py-2.5 rounded-chip text-sm font-mono hover:bg-border transition-colors"
                >
                  View Details
                </Link>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  )
}
