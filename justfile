# Local CI (#68, skill local-ci): four tiers, one recipe each, no GitHub and no AI agent needed.
# GitHub Actions keeps one workflow, `prod.yml`, triggered by a signed release tag (agents-skills
# ADR-0004, local-first CI/CD). Tools come from mise.toml (`just setup`); run through
# `mise x -- just <tier>` when the shell does not activate mise (the git hooks do).
#
#   L0 fast     pre-commit hook                        staged files only                         < 10 s
#   L1 check    pre-push hook, review-local --push     lint + test + security + secrets          < 3 min
#   L2 gate     review-local § 2b, on the pushed head  check + Sonar + Trivy + image + render,    5–15 min
#               before every merge                     then the attestation
#   L3 nightly  systemd user timer                     check + TruffleHog + mise outdated
#
# Then: `just merge <pr>` (refuses without the gate attestation on the head SHA), `just deploy
# staging` from up-to-date main (API on Fly.io, catalogue into Neon), `just attest staging` after
# the QA pass, a signed tag for production (`just deploy prod <tag>` is the fallback when Actions
# cannot run). The API has one Fly app and one Neon project: staging and production share them
# until a second app exists (derogation recorded in PROJECT_LOG.md, 2026-11-07).

set shell := ["sh", "-eu", "-c"]

semgrep := "uvx semgrep@1.182.1" # via uv, not mise: a mise pipx install needs a mise-managed Python
api_image := "ohm-sweet-ohm-api:gate"
renderer_image := "ohm-sweet-ohm-renderer"

# L1 by default
default: check

# Once per clone: the pinned toolchain, the dependencies and the git hooks
setup:
    mise install
    mise x -- pnpm install --frozen-lockfile
    mise x -- lefthook install

# L0 — the pre-commit checks on the staged files (< 10 s)
fast:
    lefthook run pre-commit

# Fail fast outside the .nvmrc Node major: an asdf or nvm default Node in a non-interactive shell
# would run the whole suite on the wrong runtime. Fix: `mise x -- just <recipe>`.
[private]
node-guard:
    @node -e 'const want=require("fs").readFileSync(".nvmrc","utf8").trim().split(".")[0]; const v=process.versions.node; if (v.split(".")[0] !== want) { console.error("Node " + v + " found, Node " + want + " required (.nvmrc). Run: mise x -- just <recipe>"); process.exit(1) }'

# Format, eslint, markdownlint, tsc, typos, the prod workflow, the Dockerfiles, the shell scripts, the hooks
lint: node-guard
    pnpm format:check
    pnpm lint
    pnpm lint:md
    pnpm typecheck
    typos
    actionlint
    zizmor --quiet .github/workflows
    hadolint --config .hadolint.yaml apps/api/Dockerfile docker/renderer/Dockerfile
    shellcheck --severity=warning scripts/*.sh
    lefthook validate

# Unit and integration suites (Testcontainers: Docker must run) with the per-package coverage floor
# of vitest.config.ts (80 %), the doc coverage floor (90 %) and the local CI wiring tests
test: node-guard
    pnpm test:coverage
    pnpm doc:coverage
    sh scripts/test-local-ci.sh
    sh scripts/test-attest.sh

# SAST (Semgrep Community Edition, named registry rulesets: `--config auto` would send the project
# URL; no p/secrets, which prints the matched value, gitleaks redacts it) on the shipped code and
# the scripts, then known vulnerabilities in the production dependencies, HIGH and above (the same
# policy as the former ci.yml; `just gate` adds Trivy on the lockfile). No osv-scanner: it has no
# severity threshold and would fail on dev-only tooling (markdownlint's markdown-it, katex).
# EIO_BACKEND=posix: semgrep-core otherwise opens io_uring rings, charged to the user's
# RLIMIT_MEMLOCK together with every Electron/Node process, and dies intermittently.
security:
    EIO_BACKEND=posix {{semgrep}} scan --config p/javascript --config p/typescript --config p/nodejs --error --metrics=off --quiet -j 4 apps/api/src apps/importer/src apps/web/src packages/db/src packages/domain/src packages/schemas/src scripts
    pnpm audit --prod --audit-level high

# Secrets in the whole git history
secrets:
    gitleaks git --redact --no-banner .

# L1 — pre-push (< 3 min)
check: lint test security secrets

# L2 — pre-merge, called by review-local § 2b (base: the branch to integrate into), 5–15 min.
# Docker down: the filesystem scans still run, then the recipe exits 3 before the attestation
# (incomplete, never green). Ends with the gate attestation (agents-skills ADR-0003): commit status
# `gate` + signed note on HEAD, which must already be pushed, so it runs on the pushed head only.
gate base="origin/main": check
    #!/bin/sh
    set -eu
    # The full-history gitleaks scan of `check` already covers base..HEAD.
    base={{quote(base)}}
    case "$base" in origin/*) git fetch --quiet origin "${base#origin/}" ;; esac
    just sonar
    trivy fs --exit-code 1 --severity HIGH,CRITICAL --skip-dirs node_modules,build,dist,coverage,.wrangler .
    trivy config --exit-code 1 --severity HIGH,CRITICAL --misconfig-scanners dockerfile --skip-dirs node_modules,build,dist,coverage,.wrangler .
    if ! docker info > /dev/null 2>&1; then
      echo "gate: WARNING docker unreachable, API image build, smoke, trivy image, syft SBOM, catalogue render and act not run"
      echo "gate: INCOMPLETE (exit 3) — start Docker and run just gate again before asking for a merge"
      exit 3
    fi
    docker build -q -f apps/api/Dockerfile -t {{api_image}} .
    just smoke
    trivy image --exit-code 1 --severity HIGH,CRITICAL --ignore-unfixed {{api_image}}
    syft {{api_image}} -q -o spdx-json > sbom-api.spdx.json
    echo "gate: SBOM written to sbom-api.spdx.json (gitignored)"
    just render
    changed=$(git diff --name-only --diff-filter=d "$base...HEAD" -- .github/workflows)
    if [ -z "$changed" ]; then echo "gate: no workflow added or changed, rehearse skipped"
    else printf '%s\n' "$changed" | while IFS= read -r w; do just rehearse "$w"; done; fi
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

# Proves the gate's API image starts and answers /health as the unprivileged user; the database URL
# points nowhere on purpose, the health route does not need it.
smoke:
    #!/bin/sh
    set -eu
    name=osh-api-smoke
    docker rm -f "$name" > /dev/null 2>&1 || true
    docker run -d --name "$name" -e DATABASE_URL=postgres://nobody:nothing@127.0.0.1:1/nothing {{api_image}} > /dev/null
    i=0
    while [ "$i" -lt 20 ]; do
      i=$((i + 1))
      if [ "$(docker inspect -f '{{{{.State.Health.Status}}' "$name")" = healthy ]; then
        docker rm -f "$name" > /dev/null; echo "smoke: healthy after $i s"; exit 0
      fi
      sleep 1
    done
    docker logs "$name"; docker rm -f "$name" > /dev/null; echo "smoke: not healthy after 20 s" >&2; exit 1

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
      else got=refused; fi
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

# Deploy from a clean tree (scripts/deploy.sh holds the commands). staging: up-to-date main after a
# green gate (agents-skills ADR-0002): the catalogue is rendered and imported into Neon (migrations
# inside, DATABASE_URL from the git-ignored .env.staging), then the API is deployed to Fly.io.
# prod: the fallback when Actions cannot run (agents-skills ADR-0004): classify, verify-tag, peel,
# status + notes, deployed from the tag's commit, then back to the branch.
deploy env tag="":
    #!/bin/sh
    set -eu
    env={{quote(env)}} tag={{quote(tag)}}
    [ -z "$(git status --porcelain)" ] || { echo "deploy: commit or stash local changes first" >&2; exit 1; }
    case "$env" in
      staging)
        git fetch --quiet origin main
        [ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] \
          || { echo "deploy: staging deploys from up-to-date main only" >&2; exit 1; }
        sh scripts/attest.sh verify gate HEAD
        just render
        sh scripts/deploy.sh catalogue staging
        sh scripts/deploy.sh api staging
        ;;
      prod)
        [ -n "$tag" ] || { echo "deploy: usage just deploy prod vX.Y.Z" >&2; exit 1; }
        # this recipe and attest.sh must be the trusted ones of main, never a branch's; same checks as
        # the prod workflow (.github/workflows/prod.yml)
        git fetch --quiet origin main tag "$tag"
        [ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] \
          || { echo "deploy: run the prod fallback from up-to-date main" >&2; exit 1; }
        sha=$(sh scripts/attest.sh release "$tag")
        back=$(git symbolic-ref --quiet --short HEAD || git rev-parse HEAD)
        trap 'git checkout --quiet "$back"' EXIT
        git -c advice.detachedHead=false checkout --quiet "$sha"
        sh scripts/deploy.sh api prod
        echo "deploy: prod deployed from $tag ($sha) by the local fallback: log it in PROJECT_LOG.md"
        ;;
      *) echo "deploy: unknown environment $env (staging, prod)" >&2; exit 1 ;;
    esac

# Record the staging QA pass on the deployed main commit, only after it succeeded (agents-skills ADR-0004)
attest env:
    #!/bin/sh
    set -eu
    [ {{quote(env)}} = staging ] || { echo "attest: only staging is attested" >&2; exit 1; }
    git fetch --quiet origin main
    [ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] \
      || { echo "attest: HEAD is not the deployed origin/main" >&2; exit 1; }
    sh scripts/attest.sh write deploy/staging

# L3 — nightly, systemd user timer (no time budget)
nightly: check
    trufflehog git "file://$PWD" --no-verification --fail --no-update
    mise outdated
