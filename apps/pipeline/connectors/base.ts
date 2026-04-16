// apps/pipeline/connectors/base.ts
// IConnector interface — all source connectors must implement this

export interface RawHackathon {
  sourceId: string
  title: string
  organizerName: string
  applyUrl: string
  registrationClose: string    // ISO date string
  registrationOpen?: string
  eventStart?: string
  eventEnd?: string
  description?: string
  longDescription?: string
  mode?: 'ONLINE' | 'OFFLINE' | 'HYBRID'
  entryFee?: number
  entryFeeCurrency?: string
  teamSizeMin?: number
  teamSizeMax?: number
  eligibility?: 'STUDENTS' | 'OPEN' | 'PROFESSIONALS'
  durationType?: 'HR24' | 'HR48' | 'WEEK' | 'MONTH' | 'CUSTOM'
  prizePool?: number
  prizeCurrency?: string
  prizeDescription?: string
  themeTags?: string[]
  sponsors?: string[]
  organizerLogoUrl?: string
  scope?: 'GLOBAL' | 'INDIA'
  indiaRegion?: string
}

export interface ConnectorResult {
  source: string
  records: RawHackathon[]
  errors: string[]
  status: 'SUCCESS' | 'PARTIAL' | 'FAILED'
}

export interface IConnector {
  source: string
  fetch(): Promise<ConnectorResult>
}
