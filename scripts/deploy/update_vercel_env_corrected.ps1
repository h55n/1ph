#!/usr/bin/env pwsh
# Script to update all Vercel env vars to the new Supabase project using the correct hostname

$NEW_SUPABASE_URL = "https://flwrpsoizcinyrsukpcq.supabase.co"
$NEW_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZsd3Jwc29pemNpbnlyc3VrcGNxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg0MjQ1MjAsImV4cCI6MjA5NDAwMDUyMH0.lGjheCaiHK4rdye2NrIRG4os_yfHQc_XPf8kRfuBcRY"
$NEW_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZsd3Jwc29pemNpbnlyc3VrcGNxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODQyNDUyMCwiZXhwIjoyMDk0MDAwNTIwfQ.PcHtYDjmUbYGPcHeEq2fyxLw9OfNURIJ341zWs9v5mA"

$NEW_DB_URL = "postgresql://postgres:FbXwVCKJ7k4Y6GyG@db.flwrpsoizcinyrsukpcq.supabase.co:6543/postgres?pgbouncer=true"
$NEW_DIRECT_URL = "postgresql://postgres:FbXwVCKJ7k4Y6GyG@db.flwrpsoizcinyrsukpcq.supabase.co:5432/postgres"

Write-Host "Updating DATABASE_URL..."
echo $NEW_DB_URL | npx vercel env add DATABASE_URL production
echo $NEW_DB_URL | npx vercel env add DATABASE_URL preview
echo $NEW_DB_URL | npx vercel env add DATABASE_URL development

Write-Host "Updating DIRECT_URL..."
echo $NEW_DIRECT_URL | npx vercel env add DIRECT_URL production
echo $NEW_DIRECT_URL | npx vercel env add DIRECT_URL preview
echo $NEW_DIRECT_URL | npx vercel env add DIRECT_URL development

Write-Host "Done."
