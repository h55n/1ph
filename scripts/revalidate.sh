#!/bin/bash
# Usage: ./scripts/revalidate.sh https://your-domain.vercel.app your-secret
# Or set WEB_REVALIDATE_URL and WEB_REVALIDATE_SECRET env vars

URL=${1:-$WEB_REVALIDATE_URL}
SECRET=${2:-$WEB_REVALIDATE_SECRET}

if [ -z "$URL" ] || [ -z "$SECRET" ]; then
  echo "Usage: $0 <url> <secret>"
  echo "  or set WEB_REVALIDATE_URL and WEB_REVALIDATE_SECRET env vars"
  exit 1
fi

echo "Triggering revalidation at $URL..."
curl -X POST "$URL/api/revalidate" \
  -H "Authorization: Bearer $SECRET" \
  -H "Content-Type: application/json" \
  -v
