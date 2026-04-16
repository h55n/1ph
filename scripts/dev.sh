#!/bin/bash
# scripts/dev.sh — Start dev environment

echo "🔧 Starting 1ph dev environment..."
echo "  → Web:      http://localhost:3000"
echo "  → Pipeline: http://localhost:3001"
echo ""

# Start both services via Turborepo
npx turbo dev --parallel
