#!/bin/sh
# Deploy one component to one environment (#68, agents-skills ADR-0004, local-first CI/CD): the
# command behind `just deploy staging`.
#
#   deploy.sh catalogue staging     pnpm catalogue:import into Neon, DATABASE_URL always read from
#                                   .env.staging (git-ignored, a shell value is ignored); run `just render`
#                                   first, the importer reads build/catalogue
#
# The web Worker, deployed by Workers Builds, reads the same Neon project through Hyperdrive
# (ADR-0005); there is no API to deploy any more (#111). The caller (justfile) checks the tree and
# the gate attestation.
set -eu

die() { echo "deploy: $*" >&2; exit 1; }
[ $# -eq 2 ] || die "usage: deploy.sh catalogue staging"
component=$1 env=$2
case "$env" in staging|prod) ;; *) die "unknown environment $env (staging, prod)" ;; esac
root=$(cd "$(dirname "$0")/.." && pwd)
cd "$root"

case "$component" in
  catalogue)
    [ "$env" = staging ] || die "the catalogue is imported by the staging deploy only"
    [ -d build/catalogue ] || die "build/catalogue missing: run just render first"
    # Always the file, never a DATABASE_URL left in the shell (the README local example would win).
    [ -f .env.staging ] || die "no .env.staging (docs/deploy.md § Neon)"
    DATABASE_URL=$(sed -n 's/^DATABASE_URL=//p' .env.staging | head -n 1 | tr -d '\r' | sed -e "s/^['\"]//" -e "s/['\"]$//")
    [ -n "$DATABASE_URL" ] || die "no DATABASE_URL line in .env.staging"
    export DATABASE_URL
    pnpm catalogue:import
    ;;
  *) die "unknown component $component (catalogue)" ;;
esac
