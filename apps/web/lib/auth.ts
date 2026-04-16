import { NextAuthOptions } from 'next-auth'
import GoogleProvider from 'next-auth/providers/google'
import GitHubProvider from 'next-auth/providers/github'
import { PrismaAdapter } from '@next-auth/prisma-adapter'
import type { JWT } from 'next-auth/jwt'
import { prisma } from './db'

export const authOptions: NextAuthOptions = {
  adapter: PrismaAdapter(prisma),
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    GitHubProvider({
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      const typedToken = token as JWT & { role?: string }
      if (user) {
        typedToken.role = ((user as { role?: string }).role ?? 'VISITOR')
      }
      return typedToken
    },
    async session({ session, token }) {
      if (session.user) {
        const typedToken = token as JWT & { role?: string }
        const sessionUser = session.user as typeof session.user & { id?: string; role?: string }
        sessionUser.id = typedToken.sub
        sessionUser.role = typedToken.role ?? 'VISITOR'
      }
      return session
    },
  },
  pages: {
    signIn: '/login',
  },
  session: {
    strategy: 'jwt',
  },
  secret: process.env.NEXTAUTH_SECRET,
}
