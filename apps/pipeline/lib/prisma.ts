import { PrismaClient } from '@prisma/client'

declare global {
  // eslint-disable-next-line no-var
  var pipelinePrisma: PrismaClient | undefined
}

export const prisma = global.pipelinePrisma ?? new PrismaClient()

if (process.env.NODE_ENV !== 'production') {
  global.pipelinePrisma = prisma
}
