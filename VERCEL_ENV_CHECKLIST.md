# Vercel Environment Variables Checklist

Go to: Vercel Dashboard → Your Project → Settings → Environment Variables

## Required Variables

| Variable | Where to get it |
|----------|----------------|
| `DATABASE_URL` | Supabase → Settings → Database → Connection string (pooling URL, port **6543**) |
| `DIRECT_URL` | Supabase → Settings → Database → Direct connection URL (port 5432) |
| `NEXTAUTH_URL` | `https://your-domain.vercel.app` — **NOT localhost** |
| `NEXTAUTH_SECRET` | Run: `openssl rand -base64 32` |
| `GOOGLE_CLIENT_ID` | Google Cloud Console → OAuth credentials |
| `GOOGLE_CLIENT_SECRET` | Google Cloud Console → OAuth credentials |
| `GITHUB_CLIENT_ID` | GitHub → Settings → Developer settings → OAuth Apps |
| `GITHUB_CLIENT_SECRET` | GitHub → Settings → Developer settings → OAuth Apps |
| `REVALIDATE_SECRET` | Must match `WEB_REVALIDATE_SECRET` GitHub Actions secret |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase → Settings → API → Project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase → Settings → API → anon/public key |

## Common Mistakes

1. **`DATABASE_URL` must be the POOLING URL** (port **6543**), not the direct connection (port 5432)
   - Pooling: `postgresql://postgres:[password]@db.[ref].supabase.co:6543/postgres?pgbouncer=true`
   - Direct: `postgresql://postgres:[password]@db.[ref].supabase.co:5432/postgres`

2. **`NEXTAUTH_URL` must be production URL**, not `http://localhost:3000`
   - Correct: `https://1ph.vercel.app`
   - Wrong: `http://localhost:3000`

3. **After adding/changing vars**, you MUST trigger a new deployment (not just save)
   - Go to Deployments → Redeploy, OR push a new commit

4. **`NEXT_PUBLIC_*` vars** are baked at build time — always redeploy after changing them
