#!/usr/bin/env bash
# Link Postgres DATABASE_URL to the AIfy_Resume API service on Railway.
#
# Prerequisites:
#   npm install -g @railway/cli
#   railway login
#   cd backend && railway link   # select project + AIfy_Resume service
#
# Usage:
#   ./scripts/railway-link-postgres.sh
#   ./scripts/railway-link-postgres.sh "Postgres-Cq8L" "AIfy_Resume"

set -euo pipefail

POSTGRES_SERVICE="${1:-Postgres-Cq8L}"
API_SERVICE="${2:-AIfy_Resume}"

if ! command -v railway >/dev/null 2>&1; then
  echo "Install Railway CLI: npm install -g @railway/cli"
  echo "Then: railway login"
  exit 1
fi

REF='${{'"${POSTGRES_SERVICE}"'.DATABASE_URL}}'

echo "Setting DATABASE_URL=${REF} on service: ${API_SERVICE}"
railway variables --set "DATABASE_URL=${REF}" --service "${API_SERVICE}"

echo "Done. Redeploy ${API_SERVICE} if it does not auto-redeploy."
echo "Verify logs show: Database env: DATABASE_URL=set"
