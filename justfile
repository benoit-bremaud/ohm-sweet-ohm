# Local CI (#68, skill local-ci): four tiers, one recipe each, no GitHub and no AI agent needed.
# No GitHub Actions workflow (agents-skills ADR-0004, local-first CI/CD; the last one, `prod.yml`,
# deployed the removed API, #111). Tools come from mise.toml (`just setup`); run through
# `mise x -- just <tier>` when the shell does not activate mise (the git hooks do).
#
#   L0 fast     pre-commit hook                        staged files only                         < 10 s
#   L1 check    pre-push hook, review-local --push     lint + test + security + secrets          < 3 min
#   L2 gate     review-local § 2b, on the pushed head  check + Sonar + Trivy + render,           5–15 min
#               before every merge                     then the attestation
#   L3 nightly  systemd user timer                     Trivy fs + TruffleHog + live site fail; check + mise outdated warn
#
# Then: `just merge <pr>` (refuses without the gate attestation on the head SHA), `just deploy
# staging` from up-to-date main (catalogue into Neon), `just attest staging` after the QA pass. The
# web Worker reads Neon through Hyperdrive and is deployed by Cloudflare Workers Builds from `main`
# (ADR-0005): there is no API to deploy and no prod workflow any more (#111).

set shell := ["sh", "-eu", "-c"]

semgrep := "uvx semgrep@1.182.1" # via uv, not mise: a mise pipx install needs a mise-managed Python
ruff := "uvx ruff@0.15.8"
renderer_image := "ohm-sweet-ohm-renderer"
# Trivy skips: `**/node_modules` at any depth (a bare name only skips the top-level one) and the
# other checkouts under `.claude/worktrees`, each gated on its own (#175)
trivy_skip := "**/node_modules,.claude/worktrees,build,dist,coverage,.wrangler"

# L1 by default
default: check

# Once per clone: the pinned toolchain, the dependencies, the Astro types and content store, the git hooks
setup:
    mise install
    mise x -- pnpm install --frozen-lockfile
    mise x -- just sync
    mise x -- lefthook install

# Regenerate the SVG figures of the troubleshooting guides (scripts/figures, #101)
figures:
    python3 -B scripts/figures/generate.py

# Export one guide's figures as PNG, plus photo plates when photos exist (#162; needs Inkscape and
# ImageMagick 7); out/ and photos/ are git-ignored: photos of a client's board are never committed
figures-png guide out="out/figures" photos="":
    python3 -B scripts/figures/export.py {{quote("troubleshooting/" + guide)}} {{quote(out)}} {{ if photos == "" { "" } else { quote(photos) } }}

# Render the Mermaid diagrams of the guides to the committed arbre-N.svg files (#123); a test
# fails while one is stale. Re-run it after a Mermaid upgrade: the hash does not cover the
# version. Needs Chromium once: `mise x -- pnpm --filter web exec playwright install chromium`
trees:
    mise x -- node apps/web/scripts/render-trees.ts

# L0 — the pre-commit checks on the staged files (< 10 s)
fast:
    lefthook run pre-commit

# Fail fast outside the .nvmrc Node major: an asdf or nvm default Node in a non-interactive shell
# would run the whole suite on the wrong runtime. Fix: `mise x -- just <recipe>`.
[private]
node-guard:
    @node -e 'const want=require("fs").readFileSync(".nvmrc","utf8").trim().split(".")[0]; const v=process.versions.node; if (v.split(".")[0] !== want) { console.error("Node " + v + " found, Node " + want + " required (.nvmrc). Run: mise x -- just <recipe>"); process.exit(1) }'

# Generate the Astro types and the content store (.astro/): eslint needs the types, the guide page
# tests read the store (a fresh clone has neither, #135)
sync: node-guard
    pnpm -C apps/web exec astro sync

# Format, eslint, markdownlint, tsc, typos, any GitHub workflow, the Dockerfiles, the shell scripts, the
# figure generator (ruff), the hooks
lint: sync
    pnpm format:check
    pnpm lint
    pnpm lint:md
    pnpm typecheck
    typos
    if [ -d .github/workflows ]; then actionlint; zizmor --quiet .github/workflows; fi
    hadolint --config .hadolint.yaml docker/renderer/Dockerfile
    shellcheck --severity=warning scripts/*.sh
    {{ruff}} format --check scripts/figures
    {{ruff}} check scripts/figures
    lefthook validate

# Unit and integration suites (Testcontainers: Docker must run) with the per-package coverage floor
# of vitest.config.ts (80 %), the doc coverage floor (90 %), the local CI wiring tests and the
# figure generator tests (committed SVGs equal to the generated ones)
test: sync
    pnpm test:coverage
    pnpm doc:coverage
    sh scripts/test-local-ci.sh
    sh scripts/test-attest.sh
    sh scripts/test-check-live.sh
    sh scripts/test-figures.sh

# SAST (Semgrep Community Edition, named registry rulesets: `--config auto` would send the project
# URL; no p/secrets, which prints the matched value, gitleaks redacts it) on the shipped code and
# the scripts, then known vulnerabilities in every dependency, dev ones included, HIGH and above
# (pnpm.overrides in package.json pins a vulnerable transitive until its parent moves). No
# osv-scanner: it has no severity threshold, so every low finding would block.
# EIO_BACKEND=posix: semgrep-core otherwise opens io_uring rings, charged to the user's
# RLIMIT_MEMLOCK together with every Electron/Node process, and dies intermittently.
security:
    EIO_BACKEND=posix {{semgrep}} scan --config p/javascript --config p/typescript --config p/nodejs --error --metrics=off --quiet -j 4 apps/importer/src apps/web/src packages/db/src packages/domain/src packages/schemas/src scripts
    pnpm audit --audit-level high

# Secrets in the whole git history
secrets:
    gitleaks git --redact --no-banner .

# L1 — pre-push (< 3 min)
check: lint test security secrets

# L2 — pre-merge, called by review-local § 2b (base: the branch to integrate into), 5–15 min.
# Docker down: the filesystem scans still run, then the recipe exits 3 before the attestation
# (incomplete, never green). Ends with the gate attestation (agents-skills ADR-0003): commit status
# `gate` + signed note on HEAD, which must already be pushed, so it runs on the pushed head only.
gate base="origin/main":
    #!/bin/sh
    set -eu
    # `check` runs from the body, not as a dependency, so the HEAD it checked is the one attested.
    start=$(git rev-parse HEAD)
    just check
    # The full-history gitleaks scan of `check` already covers base..HEAD.
    base={{quote(base)}}
    case "$base" in origin/*) git fetch --quiet origin "${base#origin/}" ;; esac
    just sonar
    trivy fs --exit-code 1 --severity HIGH,CRITICAL --ignorefile .trivyignore.yaml --skip-dirs '{{trivy_skip}}' .
    trivy config --exit-code 1 --severity HIGH,CRITICAL --misconfig-scanners dockerfile --skip-dirs '{{trivy_skip}}' .
    if ! docker info > /dev/null 2>&1; then
      echo "gate: WARNING docker unreachable, catalogue render and act not run"
      echo "gate: INCOMPLETE (exit 3) — start Docker and run just gate again before asking for a merge"
      exit 3
    fi
    just render
    changed=$(git diff --name-only --diff-filter=d "$base...HEAD" -- .github/workflows)
    if [ -z "$changed" ]; then echo "gate: no workflow added or changed, rehearse skipped"
    else printf '%s\n' "$changed" | while IFS= read -r w; do just rehearse "$w"; done; fi
    [ "$(git rev-parse HEAD)" = "$start" ] || { echo "gate: HEAD moved during the gate ($start checked), run it again" >&2; exit 1; }
    sh scripts/attest.sh write gate

# SonarQube analysis on the shared self-hosted instance with the machine's global analysis token
# (never a per-project one; skill infra-accounts), waiting for the quality gate. It uploads
# coverage/lcov.info, so it refuses a report older than the sources: `just test` writes it first.
sonar:
    #!/bin/sh
    set -eu
    command -v sonar-scanner > /dev/null || { echo "sonar: sonar-scanner not on PATH (system tool, skill local-ci rule 2)" >&2; exit 1; }
    [ -f coverage/lcov.info ] || { echo "sonar: run just test first (coverage/lcov.info missing)" >&2; exit 1; }
    stale=$(find apps packages -path '*/node_modules' -prune -o -path '*/src/*' -newer coverage/lcov.info -print -quit)
    [ -z "$stale" ] || { echo "sonar: coverage/lcov.info is older than $stale; run just test" >&2; exit 1; }
    SONAR_TOKEN="${SONAR_TOKEN:-$(cat "$HOME/.config/sonarqube/analysis-token" 2>/dev/null || true)}"
    [ -n "$SONAR_TOKEN" ] || { echo "sonar: no token in SONAR_TOKEN or ~/.config/sonarqube/analysis-token" >&2; exit 1; }
    SONAR_TOKEN="$SONAR_TOKEN" sonar-scanner -Dsonar.host.url="${SONAR_HOST_URL:-http://localhost:9000}"

# Render every catalogue schematic to a cropped SVG under build/catalogue (renderer image: KiCad and
# Inkscape, ADR-0002) and check one SVG per schematic. `just deploy staging` imports the result.
render:
    #!/bin/sh
    set -eu
    docker build -q -t {{renderer_image}} docker/renderer
    mkdir -p build
    docker run --rm -u "$(id -u):$(id -g)" -e HOME=/tmp -v "$PWD:/repo" -w /repo --entrypoint scripts/render-catalogue.sh {{renderer_image}}
    expected=$(find catalogue -name schematic.kicad_sch | wc -l)
    actual=$(find build/catalogue -name schematic.svg -size +1k | wc -l)
    echo "render: schematics $expected, rendered $actual"
    [ "$expected" -eq "$actual" ]

# Rehearse a workflow with act (L2, needs docker): dry run of the whole graph, then for the prod
# workflow (agents-skills ADR-0004) a real run of its `classify` job on fake tag events. The deploy
# job never runs and act gets no secret. The tag prefix is read from the workflow's PREFIX.
rehearse workflow:
    #!/bin/sh
    set -eu
    w={{quote(workflow)}} img=ubuntu-latest=catthehacker/ubuntu:act-24.04 dir=$(git rev-parse --git-dir)
    act --dryrun -P "$img" -W "$w" < /dev/null
    grep -q '^  classify:' "$w" || exit 0
    p=$(sed -n 's/^  PREFIX: *\([^ #]*\).*/\1/p' "$w" | tr -d "'\"")
    trap 'rm -f "$dir/act-event.json" "$dir/act.log"' EXIT
    for case in "${p}1.2.3:stable" "${p}1.2.3-rc.1:prerelease" not-a-tag:refused; do
      tag=${case%:*} want=${case##*:}
      printf '{"ref":"refs/tags/%s"}\n' "$tag" > "$dir/act-event.json"
      if act push -e "$dir/act-event.json" -j classify -P "$img" -W "$w" < /dev/null > "$dir/act.log" 2>&1
      then got=$(sed -n 's/.*::set-output:: channel=//p' "$dir/act.log" | tail -1) # act 0.2.92 log format
      elif grep -q "not a release tag" "$dir/act.log"; then got=refused
      else got=error; fi
      [ "$got" = "$want" ] || { cat "$dir/act.log"; echo "rehearse: $tag gave '$got', expected $want" >&2; exit 1; }
    done
    echo "rehearse: $w classify ok (stable, prerelease, refused)"

# Merge a PR only when its exact head SHA carries the gate attestation (agents-skills ADR-0003)
merge pr:
    #!/bin/sh
    set -eu
    sha=$(gh pr view {{quote(pr)}} --json headRefOid -q .headRefOid)
    git fetch --quiet origin "$sha"
    sh scripts/attest.sh verify gate "$sha"
    gh pr merge {{quote(pr)}} --squash --match-head-commit "$sha"

# Deploy from a clean tree (scripts/deploy.sh holds the commands): up-to-date main after a green
# gate (agents-skills ADR-0002); the catalogue is rendered and imported into Neon (migrations
# inside, DATABASE_URL from the git-ignored .env.staging). The web Worker is deployed by Workers
# Builds on every push to main and reads Neon through Hyperdrive (ADR-0005).
deploy env:
    #!/bin/sh
    set -eu
    [ {{quote(env)}} = staging ] || { echo "deploy: only staging is deployed from here (the web Worker ships through Workers Builds, ADR-0005)" >&2; exit 1; }
    [ -z "$(git status --porcelain)" ] || { echo "deploy: commit or stash local changes first" >&2; exit 1; }
    git fetch --quiet origin main
    [ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] \
      || { echo "deploy: staging deploys from up-to-date main only" >&2; exit 1; }
    sh scripts/attest.sh verify gate HEAD
    just render
    sh scripts/deploy.sh catalogue staging

# Record the staging QA pass on the deployed main commit, only after it succeeded (agents-skills ADR-0004)
attest env:
    #!/bin/sh
    set -eu
    [ {{quote(env)}} = staging ] || { echo "attest: only staging is attested" >&2; exit 1; }
    git fetch --quiet origin main
    [ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] \
      || { echo "attest: HEAD is not the deployed origin/main" >&2; exit 1; }
    sh scripts/attest.sh write deploy/staging

# L3 — nightly, systemd user timer (no time budget): new CVEs against the unchanged lockfile, deep
# secret history, the live site (#111: an outage went unseen for days), toolchain drift (`--bump`:
# without it exact pins report nothing). Vulnerabilities, secrets and an outage fail the nightly;
# lint, tests and drift only warn (agents-skills#427)
nightly:
    #!/bin/sh
    set -u
    rc=0
    warn() { "$@" || echo "WARNING nightly: '$*' failed (drift, not a failure)"; }
    warn just check
    trivy fs --exit-code 1 --severity HIGH,CRITICAL --ignorefile .trivyignore.yaml --skip-dirs '{{trivy_skip}}' . || rc=1
    trufflehog git "file://$PWD" --no-verification --fail --no-update || rc=1
    sh scripts/check-live.sh || rc=1
    warn mise outdated --bump
    exit "$rc"
