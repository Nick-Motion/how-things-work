#!/usr/bin/env bash
# Build site/ from figures/ and deploy to Cloudflare Pages. Needs .env.deploy (CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID).
set -euo pipefail
cd "$(dirname "$0")"
set -a; . ./.env.deploy; set +a
python3 build_site.py
cf pages deploy site --project-name how-things-work 2>&1 || npx -y wrangler@latest pages deploy site --project-name how-things-work
