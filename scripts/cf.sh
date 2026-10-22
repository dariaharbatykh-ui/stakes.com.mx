#!/bin/sh
# Runs Wrangler with THIS project's Cloudflare credentials, never the computer-wide login,
# so several projects on different Cloudflare accounts can't overwrite each other.
#   1. API token: .env.deploy (gitignored) with CLOUDFLARE_API_TOKEN=... -> used if set
#   2. otherwise a Wrangler login stored only for this project in .wrangler-home/ (npm run login)
# The account is pinned in wrangler.toml (account_id), so a wrong token/login fails instead of deploying elsewhere.
# Token: Cloudflare dashboard (uzivggfem-977@get-emailxyz.eu) -> My Profile -> API Tokens -> Create Token ->
#   template "Edit Cloudflare Workers" (permissions: Workers Scripts: Edit, Workers Routes: Edit (zone stakes.com.mx), Account Settings: Read).
set -e
cd "$(dirname "$0")/.."
if [ -f .env.deploy ]; then
  set -a
  . ./.env.deploy
  set +a
fi
if [ -z "$CLOUDFLARE_API_TOKEN" ]; then
  unset CLOUDFLARE_API_TOKEN
  export XDG_CONFIG_HOME="$PWD/.wrangler-home"
fi
exec npx wrangler "$@"
