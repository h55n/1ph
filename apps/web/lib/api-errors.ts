import { Prisma } from '@prisma/client'

export function isPrismaErrorCode(
  error: unknown,
  code: string
): error is Prisma.PrismaClientKnownRequestError {
  return error instanceof Prisma.PrismaClientKnownRequestError && error.code === code
}

export function logInternalApiError(operation: string, error: unknown) {
  console.error(`[api] ${operation} failed`, error)
  return { error: 'Internal server error' } as const
}
