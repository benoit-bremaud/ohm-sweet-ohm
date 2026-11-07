#!/bin/sh
# Deploy one component to one environment (#68, agents-skills ADR-0004, local-first CI/CD): the
# single command behind `just deploy staging|prod` and the `prod` GitHub workflow, so the laptop
# fallback and the tag-triggered deploy run the same thing.
#
#   deploy.sh api staging|prod      flyctl deploy of ohm-sweet-ohm-api (build context = repo root)
#   deploy.sh catalogue staging     pnpm catalogue:import into Neon, DATABASE_URL always read from
#                                   .env.staging (git-ignored, a shell value is ignored); run `just render`
#                                   first, the importer reads build/catalogue
#
# The API has one Fly app and one Neon project: staging and prod are the same target
# until a second app exists (derogation, PROJECT_LOG.md 2026-11-07). The catalogue is imported by the
# staging deploy only; a prod tag deploys the API that reads it. Credentials: flyctl session or
# FLY_API_TOKEN. The caller (justfile, workflow) checks the tree and the attestations.
set -eu

die() { echo "deploy: $*" >&2; exit 1; }
[ $# -eq 2 ] || die "usage: deploy.sh <api|catalogue> <staging|prod>"
component=$1 env=$2
case "$env" in staging|prod) ;; *) die "unknown environment $env (staging, prod)" ;; esac
root=$(cd "$(dirname "$0")/.." && pwd)
cd "$root"

case "$component" in
  api)
    command -v flyctl > /dev/null || die "flyctl not on PATH"
    # --ha=false: one Machine (two otherwise); --remote-only: Fly's builder, no local image push
    flyctl deploy --remote-only --ha=false --config apps/api/fly.toml
    ;;
  catalogue)
    [ "$env" = staging ] || die "the catalogue is imported by the staging deploy only (the prod tag deploys the API)"
    [ -d build/catalogue ] || die "build/catalogue missing: run just render first"
    # Always the file, never a DATABASE_URL left in the shell (the README local example would win).
    [ -f .env.staging ] || die "no .env.staging (docs/deploy.md § Neon)"
    DATABASE_URL=$(sed -n 's/^DATABASE_URL=//p' .env.staging | head -n 1 | tr -d '\r' | sed -e "s/^['\"]//" -e "s/['\"]$//")
    [ -n "$DATABASE_URL" ] || die "no DATABASE_URL line in .env.staging"
    export DATABASE_URL
    pnpm catalogue:import
    ;;
  *) die "unknown component $component (api, catalogue)" ;;
esac
