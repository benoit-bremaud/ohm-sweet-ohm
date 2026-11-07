#!/bin/sh
# Tests for the local CI wiring (#68, skill local-ci rule 7): the four tiers exist and compose
# (check ⊇ lint + test + security + secrets; gate and nightly ⊇ check), gate ends with the attestation
# and merge / deploy prod verify it (agents-skills ADR-0003/0004), the prod workflow is the only one
# and takes attest.sh from main, deploy.sh refuses bad arguments before any deploy command,
# lefthook.yml is valid and wires the commit-msg and pre-push hooks, the commit-msg check accepts and
# refuses the right subjects, and L0 (`just fast`) passes a clean staged change but refuses a staged
# secret and a staged typo, in a throwaway repository. Needs mise, just, lefthook, gitleaks, typos:
#   mise x -- sh scripts/test-local-ci.sh
set -e
# A hook (pre-push runs `just check`) exports these; they would aim git at the outer repository.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_PREFIX GIT_OBJECT_DIRECTORY GIT_COMMON_DIR

root=$(cd "$(dirname "$0")/.." && pwd)
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
n=0
fail() { echo "FAIL $1"; exit 1; }

# `mise x --` puts the tools on PATH but not mise itself (hooks and the throwaway repo need it).
command -v mise > /dev/null || { [ -x "$HOME/.local/bin/mise" ] && PATH="$HOME/.local/bin:$PATH" && export PATH; }
for bin in mise just lefthook gitleaks typos; do
  command -v "$bin" > /dev/null || fail "$bin not on PATH"
done

# Tiers and their composition.
cd "$root"
for r in fast check gate nightly; do
  just --show "$r" > /dev/null 2>&1 || fail "recipe $r missing"; n=$((n + 1))
done
deps() { just --show "$1" | grep -E "^$1( |:)" | sed 's/.*: *//'; } # deps <recipe>
for d in lint test security secrets; do deps check | grep -qw "$d" || fail "check lacks $d"; done
for r in gate nightly; do deps "$r" | grep -qw check || fail "$r does not depend on check"; done
for r in setup merge rehearse deploy attest render smoke sonar; do just --show "$r" > /dev/null 2>&1 || fail "recipe $r missing"; n=$((n + 1)); done
just --show gate | grep -q 'attest.sh write gate' || fail "gate does not write the attestation"
just --show merge | grep -q 'attest.sh verify gate' || fail "merge does not verify the attestation"
just --show deploy | grep -q 'attest.sh release' || fail "deploy prod skips attest.sh release"
just --show deploy | grep -q 'attest.sh verify gate HEAD' || fail "deploy staging skips the gate attestation"
just --show attest | grep -q 'attest.sh write deploy/staging' || fail "attest staging does not write the note"
wf=.github/workflows/prod.yml
[ "$(find .github/workflows -name '*.yml' -o -name '*.yaml' | wc -l)" -eq 1 ] || fail "more than one GitHub workflow (agents-skills ADR-0004: prod.yml only)"
grep -q 'git show origin/main:scripts/attest.sh' "$wf" || fail "prod workflow does not take attest.sh from main"
grep -q 'attest.sh" release' "$wf" || fail "prod workflow does not run attest.sh release"
grep -q 'scripts/deploy.sh api prod' "$wf" || fail "prod workflow does not run scripts/deploy.sh api prod"
e3=$(just --show gate | grep -n 'exit 3' | head -1 | cut -d: -f1); at=$(just --show gate | grep -n 'attest.sh write gate' | cut -d: -f1)
[ -n "$e3" ] && [ -n "$at" ] && [ "$e3" -lt "$at" ] || fail "gate must exit 3 (Docker down) before it writes the attestation"
n=$((n + 10))
# deploy.sh refusals: no network, exit 1 and a message, before any deploy command runs.
refuse() { # refuse <args…>: deploy.sh must exit 1 and say "deploy:"
  if out=$(sh scripts/deploy.sh "$@" 2>&1); then fail "deploy.sh $* did not refuse"; fi
  case "$out" in deploy:*) ;; *) fail "deploy.sh $* refused without the deploy: prefix: $out" ;; esac
  n=$((n + 1))
}
refuse; refuse api; refuse api qa; refuse web prod; refuse catalogue prod
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
