#!/usr/bin/env pwsh
# Restore Vercel environment variables to the OLD Supabase project
# because we have the password for it and it works perfectly.

$OLD_SUPABASE_URL = "https://ddgyulnvbdiczmzggkmx.supabase.co"
$OLD_ANON_KEY = "sb_publishable_PbXEinmd-Z4NmES2t4I7ow_2TWfBR5U"
$OLD_SERVICE_KEY = "REDACTED_SECRET"
$OLD_DB_URL = "postgresql://postgres:REDACTED_DB_PASSWORD@db.ddgyulnvbdiczmzggkmx.supabase.co:5432/postgres"

Write-Host "Removing any existing vars..."
npx vercel env rm DATABASE_URL production --yes 2>$null
npx vercel env rm DIRECT_URL production --yes 2>$null
npx vercel env rm NEXT_PUBLIC_SUPABASE_URL production --yes 2>$null
npx vercel env rm NEXT_PUBLIC_SUPABASE_ANON_KEY production --yes 2>$null
npx vercel env rm NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY production --yes 2>$null
npx vercel env rm SUPABASE_SERVICE_KEY production --yes 2>$null

Write-Host "Adding old reliable DATABASE_URL..."
echo $OLD_DB_URL | npx vercel env add DATABASE_URL production
echo $OLD_DB_URL | npx vercel env add DIRECT_URL production

Write-Host "Adding old reliable NEXT_PUBLIC_SUPABASE_URL..."
echo $OLD_SUPABASE_URL | npx vercel env add NEXT_PUBLIC_SUPABASE_URL production

Write-Host "Adding old reliable keys..."
echo $OLD_ANON_KEY | npx vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production
echo $OLD_ANON_KEY | npx vercel env add NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY production
echo $OLD_SERVICE_KEY | npx vercel env add SUPABASE_SERVICE_KEY production

Write-Host "Done! Vercel is now configured with the working database."
