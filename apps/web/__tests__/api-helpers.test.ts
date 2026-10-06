import { Prisma } from '@prisma/client'
import { isPrismaErrorCode } from '../lib/api-errors'
import { readHackathonId } from '../lib/api-validation'

function requestWithBody(body: string) {
  return {
    json: async () => {
      try {
        return JSON.parse(body) as unknown
      } catch {
        throw new SyntaxError('Invalid JSON')
      }
    },
  }
}

describe('readHackathonId', () => {
  it('trims and returns a non-empty string ID', async () => {
    await expect(readHackathonId(requestWithBody('{"hackathonId":"  event-123  "}')))
      .resolves.toBe('event-123')
  })

  it.each([
    '{',
    'null',
    '[]',
    '{}',
    '{"hackathonId":42}',
    '{"hackathonId":"   "}',
    `{"hackathonId":"${'x'.repeat(129)}"}`,
  ])('rejects invalid request body %s', async (body) => {
    await expect(readHackathonId(requestWithBody(body))).resolves.toBeNull()
  })
})

describe('isPrismaErrorCode', () => {
  it('matches a specific known Prisma error code', () => {
    const duplicateError = new Prisma.PrismaClientKnownRequestError('duplicate', {
      code: 'P2002',
      clientVersion: 'test',
    })

    expect(isPrismaErrorCode(duplicateError, 'P2002')).toBe(true)
    expect(isPrismaErrorCode(duplicateError, 'P2025')).toBe(false)
    expect(isPrismaErrorCode(new Error('database unavailable'), 'P2002')).toBe(false)
  })
})
