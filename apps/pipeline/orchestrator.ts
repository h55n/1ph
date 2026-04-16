// apps/pipeline/orchestrator.ts
// Main pipeline runner — called by scheduler for each source

import { PrismaClient } from '@prisma/client'
import type { IConnector } from './connectors/base'
import { normalize } from './normalizer/index'
import { runQualityGate } from './quality-gate/index'
import { assignTier } from './tier-engine/index'
import { logPipelineRun } from './logger/pipeline-run'

const prisma = new PrismaClient()

export async function runConnector(connector: IConnector): Promise<void> {
  console.log(`[${connector.source}] Starting...`)
  const start = Date.now()

  let newCount = 0
  let updatedCount = 0
  const closedCount = 0
  const errors: string[] = []

  try {
    const result = await connector.fetch()
    errors.push(...result.errors)

    for (const raw of result.records) {
      try {
        // Normalize
        const normalized = normalize(raw, connector.source)
        if (!normalized) {
          errors.push(`Normalization failed for sourceId: ${raw.sourceId}`)
          continue
        }

        // Quality gate
        const qResult = await runQualityGate(raw)
        if (!qResult.pass) {
          console.log(`[${connector.source}] REJECTED: ${raw.title} — ${qResult.reason}`)
          continue
        }

        // Assign prestige tier
        const prestigeTier = assignTier({
          organizerName: normalized.organizerName,
          title: normalized.title,
          prizePool: normalized.prizePool,
          prizeCurrency: normalized.prizeCurrency,
          sponsors: normalized.sponsors,
          source: connector.source,
        })

        // Compute status
        const now = new Date()
        const sevenDays = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000)
        let status: 'UPCOMING' | 'OPEN' | 'CLOSING_SOON' | 'CLOSED' = 'OPEN'
        if (normalized.registrationClose < now) status = 'CLOSED'
        else if (normalized.registrationClose <= sevenDays) status = 'CLOSING_SOON'
        else if (normalized.registrationOpen && normalized.registrationOpen > now) status = 'UPCOMING'

        // Upsert
        const existing = await prisma.hackathon.findFirst({
          where: {
            OR: [
              { source: connector.source as any, sourceId: normalized.sourceId },
              { slug: normalized.slug },
            ],
          },
          select: { id: true },
        })

        if (existing) {
          await prisma.hackathon.update({
            where: { id: existing.id },
            data: {
              title: normalized.title,
              organizerName: normalized.organizerName,
              organizerLogoUrl: normalized.organizerLogoUrl,
              description: normalized.description,
              longDescription: normalized.longDescription,
              themeTags: normalized.themeTags,
              mode: normalized.mode as any,
              entryFee: normalized.entryFee,
              entryFeeCurrency: normalized.entryFeeCurrency,
              teamSizeMin: normalized.teamSizeMin,
              teamSizeMax: normalized.teamSizeMax,
              eligibility: normalized.eligibility as any,
              durationType: normalized.durationType as any,
              prizePool: normalized.prizePool,
              prizeCurrency: normalized.prizeCurrency,
              prizeDescription: normalized.prizeDescription,
              registrationOpen: normalized.registrationOpen,
              registrationClose: normalized.registrationClose,
              eventStart: normalized.eventStart,
              eventEnd: normalized.eventEnd,
              applyUrl: normalized.applyUrl,
              scope: normalized.scope as any,
              indiaRegion: normalized.indiaRegion,
              prestigeTier: prestigeTier as any,
              sponsors: normalized.sponsors,
              status: status as any,
              lastSyncedAt: new Date(),
              urlHealthFails: 0,
            },
          })
          updatedCount++
        } else {
          await prisma.hackathon.create({
            data: {
              title: normalized.title,
              slug: normalized.slug,
              organizerName: normalized.organizerName,
              organizerLogoUrl: normalized.organizerLogoUrl,
              description: normalized.description,
              longDescription: normalized.longDescription,
              themeTags: normalized.themeTags,
              mode: normalized.mode as any,
              entryFee: normalized.entryFee,
              entryFeeCurrency: normalized.entryFeeCurrency,
              teamSizeMin: normalized.teamSizeMin,
              teamSizeMax: normalized.teamSizeMax,
              eligibility: normalized.eligibility as any,
              durationType: normalized.durationType as any,
              prizePool: normalized.prizePool,
              prizeCurrency: normalized.prizeCurrency,
              prizeDescription: normalized.prizeDescription,
              registrationOpen: normalized.registrationOpen,
              registrationClose: normalized.registrationClose,
              eventStart: normalized.eventStart,
              eventEnd: normalized.eventEnd,
              applyUrl: normalized.applyUrl,
              source: connector.source as any,
              sourceId: normalized.sourceId,
              scope: normalized.scope as any,
              indiaRegion: normalized.indiaRegion,
              prestigeTier: prestigeTier as any,
              sponsors: normalized.sponsors,
              status: status as any,
              isVerified: false,
              isFeatured: false,
              lastSyncedAt: new Date(),
            },
          })
          newCount++
        }
      } catch (err) {
        errors.push(`Upsert error for ${raw.title}: ${err}`)
      }
    }

    const elapsed = Date.now() - start
    console.log(`[${connector.source}] Done in ${elapsed}ms — new: ${newCount}, updated: ${updatedCount}, errors: ${errors.length}`)

    await logPipelineRun({
      source: connector.source,
      status: errors.length === 0 ? 'SUCCESS' : result.records.length === 0 ? 'FAILED' : 'PARTIAL',
      newCount,
      updatedCount,
      closedCount,
      errorLog: errors.length > 0 ? errors.slice(0, 20).join('\n') : undefined,
    })
  } catch (err) {
    console.error(`[${connector.source}] FATAL:`, err)
    await logPipelineRun({
      source: connector.source,
      status: 'FAILED',
      newCount: 0,
      updatedCount: 0,
      closedCount: 0,
      errorLog: String(err),
    })
  } finally {
    await prisma.$disconnect()
  }
}
