const MAX_HACKATHON_ID_LENGTH = 128

type JsonRequest = { json: () => Promise<unknown> }

export function normalizeHackathonId(value: unknown): string | null {
  if (typeof value !== 'string') return null

  const hackathonId = value.trim()
  if (hackathonId.length === 0 || hackathonId.length > MAX_HACKATHON_ID_LENGTH) {
    return null
  }

  return hackathonId
}

export async function readHackathonId(request: JsonRequest): Promise<string | null> {
  let body: unknown
  try {
    body = await request.json()
  } catch {
    return null
  }

  if (body === null || typeof body !== 'object' || Array.isArray(body)) return null
  return normalizeHackathonId((body as Record<string, unknown>).hackathonId)
}
