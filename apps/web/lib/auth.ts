import type { User as SupabaseUser } from '@supabase/supabase-js'
import { prisma } from './db'
import { createSupabaseServerClient } from './supabase/server'

const adminEmails = new Set(
  (process.env.ADMIN_EMAILS ?? '')
    .split(',')
    .map((email) => email.trim().toLowerCase())
    .filter(Boolean)
)

function providerFromUser(user: SupabaseUser) {
  const provider = user.app_metadata?.provider
  if (provider === 'github') return 'GITHUB'
  if (provider === 'google') return 'GOOGLE'
  return 'CREDENTIALS'
}

export function isAdminEmail(email?: string | null) {
  return Boolean(email && adminEmails.has(email.toLowerCase()))
}

export async function getSupabaseUser() {
  const supabase = await createSupabaseServerClient()
  const { data, error } = await supabase.auth.getUser()
  if (error || !data.user) return null
  return data.user
}

export async function requireSupabaseUser() {
  const user = await getSupabaseUser()
  if (!user) return null

  const email = user.email ?? ''
  const name = user.user_metadata?.full_name ?? user.user_metadata?.name ?? email.split('@')[0] ?? 'Builder'
  const role = isAdminEmail(email) ? 'ADMIN' : 'VISITOR'

  await prisma.user.upsert({
    where: { id: user.id },
    update: {
      email,
      name,
      avatarUrl: user.user_metadata?.avatar_url ?? null,
      role,
      provider: providerFromUser(user) as 'GOOGLE' | 'GITHUB' | 'CREDENTIALS',
    },
    create: {
      id: user.id,
      email,
      name,
      avatarUrl: user.user_metadata?.avatar_url ?? null,
      role,
      provider: providerFromUser(user) as 'GOOGLE' | 'GITHUB' | 'CREDENTIALS',
    },
  })

  return { user, role }
}
