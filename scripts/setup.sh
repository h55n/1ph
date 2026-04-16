#!/bin/bash
# scripts/setup.sh — 1ph first-time setup

set -e

echo "🚀 Setting up 1ph..."

# Check Node version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
  echo "❌ Node.js 18+ required. Current: $(node -v)"
  exit 1
fi
echo "✅ Node.js $(node -v)"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Set up env files
if [ ! -f apps/web/.env.local ]; then
  cp .env.example apps/web/.env.local
  echo "📝 Created apps/web/.env.local — fill in your values"
fi

if [ ! -f apps/pipeline/.env ]; then
  cp .env.example apps/pipeline/.env
  echo "📝 Created apps/pipeline/.env — fill in your values"
fi

# Generate Prisma client
echo "🗄️  Generating Prisma client..."
cd packages/db
npx prisma generate
cd ../..

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Fill in apps/web/.env.local with your Supabase + OAuth credentials"
echo "  2. Fill in apps/pipeline/.env with DATABASE_URL + REDIS_URL"
echo "  3. Run: npx prisma migrate dev --name init (from packages/db/)"
echo "  4. Run: ./scripts/dev.sh to start the dev server"
echo "  5. Open MASTER_PROMPT.md and paste into your coding agent"
