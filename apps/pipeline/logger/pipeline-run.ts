// apps/pipeline/logger/pipeline-run.ts
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

export async function logPipelineRun(opts: {
  source: string
  status: 'SUCCESS' | 'PARTIAL' | 'FAILED'
  newCount: number
  updatedCount: number
  closedCount: number
  errorLog?: string
}) {
  try {
    await prisma.pipelineRun.create({
      data: {
        source: opts.source as any,
        status: opts.status,
        newCount: opts.newCount,
        updatedCount: opts.updatedCount,
        closedCount: opts.closedCount,
        errorLog: opts.errorLog,
      },
    })
  } catch (err) {
    console.error('Failed to log pipeline run:', err)
  }
}
