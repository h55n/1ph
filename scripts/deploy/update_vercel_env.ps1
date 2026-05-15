#!/usr/bin/env pwsh
# Fix Vercel environment variables for new Supabase project
# Run this script to update all env vars

$NEW_SUPABASE_URL = "https://flwrpsoizcinyrsukpcq.supabase.co"
$NEW_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZsd3Jwc29pemNpbnlyc3VrcGNxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg0MjQ1MjAsImV4cCI6MjA5NDAwMDUyMH0.lGjheCaiHK4rdye2NrIRG4os_yfHQc_XPf8kRfuBcRY"
$NEW_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZsd3Jwc29pemNpbnlyc3VrcGNxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODQyNDUyMCwiZXhwIjoyMDk0MDAwNTIwfQ.PcHtYDjmUbYGPcHeEq2fyxLw9OfNURIJ341zWs9v5mA"

# IMPORTANT: Replace DB_PASSWORD below with actual password from Supabase dashboard
$DB_PASSWORD = "PLACEHOLDER_REPLACE_ME"

$NEW_DB_URL = "postgresql://postgres.flwrpsoizcinyrsukpcq:${DB_PASSWORD}@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"
$NEW_DIRECT_URL = "postgresql://postgres.flwrpsoizcinyrsukpcq:${DB_PASSWORD}@aws-0-ap-south-1.pooler.supabase.com:5432/postgres"

Write-Host "Removing old DATABASE_URL..."
npx vercel env rm DATABASE_URL production --yes 2>$null
npx vercel env rm DATABASE_URL preview --yes 2>$null
npx vercel env rm DATABASE_URL development --yes 2>$null

Write-Host "Removing old DIRECT_URL..."
npx vercel env rm DIRECT_URL production --yes 2>$null
npx vercel env rm DIRECT_URL preview --yes 2>$null
npx vercel env rm DIRECT_URL development --yes 2>$null

Write-Host "Removing old Supabase URL..."
npx vercel env rm NEXT_PUBLIC_SUPABASE_URL production --yes 2>$null
npx vercel env rm NEXT_PUBLIC_SUPABASE_URL preview --yes 2>$null
npx vercel env rm NEXT_PUBLIC_SUPABASE_URL development --yes 2>$null

Write-Host "Removing old Supabase anon key..."
npx vercel env rm NEXT_PUBLIC_SUPABASE_ANON_KEY production --yes 2>$null
npx vercel env rm NEXT_PUBLIC_SUPABASE_ANON_KEY preview --yes 2>$null
npx vercel env rm NEXT_PUBLIC_SUPABASE_ANON_KEY development --yes 2>$null

Write-Host "Removing old publishable key..."
npx vercel env rm NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY production --yes 2>$null
npx vercel env rm NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY preview --yes 2>$null
npx vercel env rm NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY development --yes 2>$null

Write-Host "Removing old service key..."
npx vercel env rm SUPABASE_SERVICE_KEY production --yes 2>$null
npx vercel env rm SUPABASE_SERVICE_KEY preview --yes 2>$null
npx vercel env rm SUPABASE_SERVICE_KEY development --yes 2>$null

Write-Host "Adding new DATABASE_URL..."
echo $NEW_DB_URL | npx vercel env add DATABASE_URL production
echo $NEW_DB_URL | npx vercel env add DATABASE_URL preview
echo $NEW_DB_URL | npx vercel env add DATABASE_URL development

Write-Host "Adding new DIRECT_URL..."
echo $NEW_DIRECT_URL | npx vercel env add DIRECT_URL production
echo $NEW_DIRECT_URL | npx vercel env add DIRECT_URL preview
echo $NEW_DIRECT_URL | npx vercel env add DIRECT_URL development

Write-Host "Adding new NEXT_PUBLIC_SUPABASE_URL..."
echo $NEW_SUPABASE_URL | npx vercel env add NEXT_PUBLIC_SUPABASE_URL production
echo $NEW_SUPABASE_URL | npx vercel env add NEXT_PUBLIC_SUPABASE_URL preview
echo $NEW_SUPABASE_URL | npx vercel env add NEXT_PUBLIC_SUPABASE_URL development

Write-Host "Adding new NEXT_PUBLIC_SUPABASE_ANON_KEY..."
echo $NEW_ANON_KEY | npx vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production
echo $NEW_ANON_KEY | npx vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY preview
echo $NEW_ANON_KEY | npx vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY development

Write-Host "Adding new NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY..."
echo $NEW_ANON_KEY | npx vercel env add NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY production
echo $NEW_ANON_KEY | npx vercel env add NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY preview
echo $NEW_ANON_KEY | npx vercel env add NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY development

Write-Host "Adding new SUPABASE_SERVICE_KEY..."
echo $NEW_SERVICE_KEY | npx vercel env add SUPABASE_SERVICE_KEY production
echo $NEW_SERVICE_KEY | npx vercel env add SUPABASE_SERVICE_KEY preview
echo $NEW_SERVICE_KEY | npx vercel env add SUPABASE_SERVICE_KEY development

Write-Host "Done! All env vars updated."
Write-Host "Next steps:"
Write-Host "1. Run Prisma migration: cd packages/db && npx prisma db push"
Write-Host "2. Run data pipeline to populate DB"
Write-Host "3. git push to trigger redeploy"
