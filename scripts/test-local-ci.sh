#!/bin/sh
# Tests for the local CI wiring (#68, skill local-ci rule 7): the four tiers exist and compose
# (check ⊇ lint + test + security + secrets; gate ⊇ check; nightly runs check as a warning and fails
# only on Trivy, TruffleHog and the live site check, agents-skills#427, #111), gate ends with the
# attestation and merge / deploy staging verify it (agents-skills ADR-0003/0004), no GitHub
# workflow is left (#111), deploy.sh refuses bad arguments before any deploy command,
# lint and test sync the Astro store first (#135), the Trivy skip list skips nested node_modules and worktrees but not a project Dockerfile (#175), lefthook.yml is valid and wires the commit-msg and pre-push hooks, the commit-msg check accepts and
# refuses the right subjects, and L0 (`just fast`) passes a clean staged change but refuses a staged
# secret and a staged typo, in a throwaway repository. Needs mise, just, lefthook, gitleaks, typos, trivy:
#   mise x -- sh scripts/test-local-ci.sh
set -e
# A hook (pre-push runs `just check`) exports these; they would aim git at the outer repository.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_PREFIX GIT_OBJECT_DIRECTORY GIT_COMMON_DIR
# The user's global config must not leak in (gpgSign, hooksPath, templateDir) (#94).
GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_CONFIG_GLOBAL GIT_CONFIG_NOSYSTEM

root=$(cd "$(dirname "$0")/.." && pwd)
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
n=0
fail() { echo "FAIL $1"; exit 1; }

# `mise x --` puts the tools on PATH but not mise itself (hooks and the throwaway repo need it).
command -v mise > /dev/null || { [ -x "$HOME/.local/bin/mise" ] && PATH="$HOME/.local/bin:$PATH" && export PATH; }
for bin in mise just lefthook gitleaks typos trivy; do
  command -v "$bin" > /dev/null || fail "$bin not on PATH"
done

# Tiers and their composition.
cd "$root"
for r in fast check gate nightly; do
  just --show "$r" > /dev/null 2>&1 || fail "recipe $r missing"; n=$((n + 1))
done
deps() { just --show "$1" | grep -E "^$1( |:)" | sed 's/.*: *//'; } # deps <recipe>
for d in lint test security secrets; do deps check | grep -qw "$d" || fail "check lacks $d"; done
for r in lint test; do deps "$r" | grep -qw sync || fail "$r does not run sync first"; done # #135
grep -q "cacheDir: './.astro'" apps/web/astro.config.ts || fail "web cacheDir is not .astro: sync writes the store where the tests do not read it"
just --show sync | grep -q 'astro sync' || fail "sync does not run astro sync"
just --show nightly | grep -q '^    warn just check$' || fail "nightly does not run check as a warning"
for t in 'trivy fs' 'trufflehog git' 'check-live.sh'; do
  just --show nightly | grep "$t" | grep -q '|| rc=1$' || fail "nightly does not fail on $t"
done
for r in gate nightly; do
  just --show "$r" | grep 'trivy fs' | grep -q -- '--ignorefile .trivyignore.yaml' || fail "$r trivy fs does not pass --ignorefile .trivyignore.yaml"
done
for r in gate nightly; do # every Trivy scan takes the shared skip list, quoted (sh must not expand the glob)
  [ "$(just --show "$r" | grep -c 'trivy ')" = "$(just --show "$r" | grep 'trivy ' | grep -cE -- "--skip-dirs '\{\{ ?trivy_skip ?\}\}'")" ] || fail "$r has a Trivy scan without --skip-dirs '{{trivy_skip}}'"
done
# The skip list on a throwaway tree (#175): Dockerfiles running as root in a nested node_modules and
# in another worktree are skipped, the same Dockerfile in the project is still reported.
for d in apps/web/node_modules/p .claude/worktrees/x/node_modules/.pnpm/p .claude/worktrees/x/docker docker/renderer; do
  mkdir -p "$work/trivy/$d" && printf 'FROM alpine:3.20\nRUN apk add curl\n' > "$work/trivy/$d/Dockerfile"
done
rc=0
(cd "$work/trivy" && trivy config --quiet --exit-code 1 --severity HIGH,CRITICAL --misconfig-scanners dockerfile --skip-dirs "$(just --justfile "$root/justfile" --evaluate trivy_skip)" .) > "$work/trivy.out" 2>&1 || rc=$?
[ "$rc" -eq 1 ] || { cat "$work/trivy.out"; fail "trivy config misses a project Dockerfile running as root (exit $rc, expected 1)"; }
[ "$(grep -c 'Dockerfile (dockerfile)' "$work/trivy.out")" = 1 ] && grep -q '^docker/renderer/Dockerfile (dockerfile)' "$work/trivy.out" \
  || { cat "$work/trivy.out"; fail "trivy config must report docker/renderer/Dockerfile only (nested node_modules and worktrees skipped)"; }
n=$((n + 4))
[ -f .trivyignore.yaml ] || fail ".trivyignore.yaml missing (gate and nightly pass it with --ignorefile)"
ids=$(grep -c '^  - id:' .trivyignore.yaml || true)
[ "$ids" = "$(grep -cE '^    (paths|purls):' .trivyignore.yaml || true)" ] || fail ".trivyignore.yaml entry without a scope (paths or purls)"
[ "$ids" = "$(grep -c '^    expired_at:' .trivyignore.yaml || true)" ] || fail ".trivyignore.yaml entry without expired_at"
[ "$ids" = "$(grep -c '^    statement:' .trivyignore.yaml || true)" ] || fail ".trivyignore.yaml entry without statement"
n=$((n + 6))
just --show nightly | tail -1 | grep -q '^    exit "$rc"$' || fail "nightly does not end with exit \"\$rc\""
just --show gate | grep -q "^    just check$" || fail "gate does not run check (from its body, before the attestation)"
for r in setup merge rehearse deploy attest render sonar; do just --show "$r" > /dev/null 2>&1 || fail "recipe $r missing"; n=$((n + 1)); done
just --show gate | grep -q 'attest.sh write gate' || fail "gate does not write the attestation"
just --show merge | grep -q 'attest.sh verify gate' || fail "merge does not verify the attestation"
just --show deploy | grep -q 'attest.sh verify gate HEAD' || fail "deploy staging skips the gate attestation"
just --show deploy | grep -q 'only staging is deployed' || fail "deploy does not refuse an environment other than staging"
just --show attest | grep -q 'attest.sh write deploy/staging' || fail "attest staging does not write the note"
sed -n '/"previews"/,$p' apps/web/wrangler.jsonc | grep -q '"binding": "HYPERDRIVE"' || fail "branch previews lack the HYPERDRIVE binding (they do not inherit it, ADR-0005)"
[ "$(grep -o '"id": "[0-9a-f]*"' apps/web/wrangler.jsonc | sort -u | wc -l)" -eq 1 ] || fail "the previews Hyperdrive id differs from the production one"
[ ! -d .github/workflows ] || fail "a GitHub workflow is back (agents-skills ADR-0004, local CI only, #111)"
e3=$(just --show gate | grep -n 'exit 3' | head -1 | cut -d: -f1); at=$(just --show gate | grep -n 'attest.sh write gate' | cut -d: -f1)
[ -n "$e3" ] && [ -n "$at" ] && [ "$e3" -lt "$at" ] || fail "gate must exit 3 (Docker down) before it writes the attestation"
n=$((n + 6))
# deploy.sh refusals: no network, exit 1 and a message, before any deploy command runs.
# Stub pnpm first on PATH: a refusal that regressed would otherwise import for real.
mkdir -p "$work/stub"
printf "#!/bin/sh\ntouch \"$work/CALLED-pnpm\"\n" > "$work/stub/pnpm"; chmod +x "$work/stub/pnpm"
refuse() { # refuse <expected substring> <args…>: deploy.sh must exit 1, say "deploy: … <expected>", call nothing
  want=$1; shift
  if out=$(PATH="$work/stub:$PATH" sh scripts/deploy.sh "$@" 2>&1); then fail "deploy.sh $* did not refuse"; fi
  printf "%s" "$out" | grep -qE "^deploy:.*($want)" || fail "deploy.sh $* refused with the wrong message: $out"
  [ ! -e "$work/CALLED-pnpm" ] || fail "deploy.sh $* called a deploy command before refusing"
  n=$((n + 1))
}
refuse usage; refuse usage catalogue; refuse "unknown environment" catalogue qa; refuse "unknown component" api staging
refuse "staging deploy only" catalogue prod; refuse "run just render|no .env.staging" catalogue staging # depends on build/
# The Node pin is written in three places; they must agree.
v=$(cat .nvmrc)
grep -q "^node = \"$v\"" mise.toml && grep -q "^nodejs $v$" .tool-versions || fail "Node pins diverge from .nvmrc ($v)"
n=$((n + 1))
grep -q '{1}' lefthook.yml || fail "commit-msg hook does not pass the message file"
grep -q 'just check' lefthook.yml || fail "pre-push hook does not run just check"
n=$((n + 2))
lefthook validate > /dev/null || fail "lefthook validate"; n=$((n + 1))

# commit-msg subjects.
msg() { # msg <expected-exit> <subject>
  printf '%s\n' "$2" > "$work/msg"
  rc=0; sh scripts/check-commit-msg.sh "$work/msg" > /dev/null 2>&1 || rc=$?
  [ "$rc" -eq "$1" ] || fail "commit-msg '$2': exit $rc, expected $1"; n=$((n + 1))
}
msg 0 'ci(workflows): move every check to local CI'
msg 0 'feat!: drop the legacy endpoint'
msg 0 'Merge branch main into feat/1'
msg 1 'Wire just'
msg 1 'ci(local): ends with a period.'
msg 1 'wip: not a listed type'

# L0 in a throwaway repository holding this repository's hook config and scripts. Only the jobs that
# need no package install run (secrets, typos): the eslint / prettier / markdownlint jobs filter on
# paths this test does not stage.
repo="$work/repo"
mkdir -p "$repo" && cd "$repo"
git init -q -b main && git config user.email t@example.com && git config user.name t
cp -R "$root/scripts" "$root/lefthook.yml" "$root/justfile" "$root/typos.toml" "$root/mise.toml" "$root/mise.lock" .
mise trust -q mise.toml
git add -A && git commit -qm init --no-verify
mkdir notes

fast() { # fast <expected-exit> <label> [<text the output must hold>]
  rc=0; just fast > "$work/out" 2>&1 || rc=$?
  [ "$rc" -eq "$1" ] || { cat "$work/out"; fail "$2: exit $rc, expected $1"; }
  [ -z "${3:-}" ] || grep -qF "$3" "$work/out" || { cat "$work/out"; fail "$2: output lacks '$3'"; }
  n=$((n + 1))
}

echo 'Plain notes.' > notes/a.txt && git add notes/a.txt
fast 0 "clean staged change"

key="AKIA$(printf seed | sha256sum | cut -c1-16 | tr 'a-f0-9' 'A-FG-P')"
printf 'token %s\n' "$key" > notes/leak.txt && git add notes/leak.txt
fast 1 "staged secret refused" "leaks found"
git rm -q --cached notes/leak.txt

printf 't%sh notes\n' e > notes/b.txt && git add notes/b.txt
fast 1 "staged typo refused" "should be"

echo "test-local-ci: $n cases passed"
