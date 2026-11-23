# Deployment

How the site is deployed (ADR-0005, which supersedes ADR-0004 for the API; deployment view in
[03-component.md](architecture/diagrams/catalogue/03-component.md)). The web Worker reads the Neon
catalogue directly through a Cloudflare Hyperdrive binding: there is no API server and no Fly.io.
Since #68 every check runs locally (§ Local CI) and no GitHub workflow is left; the catalogue is
imported from the curator's machine with `just deploy staging`. Secrets never enter the
repository: they live in the git-ignored `.env.staging` and in Cloudflare.

| Part | Where | Deployed by | URL |
| --- | --- | --- | --- |
| `apps/web` | Cloudflare Workers, Worker `ohm-sweet-ohm-web` | Workers Builds (`main` → production, other branches → preview) | `https://ohm.benoitbremaud.fr` (custom domain; `https://ohm-sweet-ohm-web.bbd-concept.workers.dev` still answers), preview URL commented on the PR |
| Hyperdrive | Cloudflare, config `ohm-sweet-ohm-catalogue`, binding `HYPERDRIVE` | once, by hand (§ Hyperdrive) | — |
| PostgreSQL | Neon, project `ohm-sweet-ohm`, free plan, `eu-central-1` | `just deploy staging` from up-to-date `main` after a green `just gate`: `just render`, then `pnpm catalogue:import` with `DATABASE_URL` from `.env.staging` | — |

Staging and production are the same Worker and the same Neon project. Migrations run in the
importer only; the Worker assumes the schema is there. Workers Builds deploys the Worker on the
merge, before anyone runs the import, so a migration ships expand-first: it is imported with
`just deploy staging` before the PR whose Worker code reads it is merged (ADR-0005). The Worker sees a new import within 5
seconds of its version check; the Hyperdrive query cache is disabled (ADR-0005).

## Secrets and variables

| Name | Where | Value | Used by |
| --- | --- | --- | --- |
| `DATABASE_URL` | `.env.staging` at the repository root, git-ignored | Neon **direct** connection string (no `-pooler`), with `?sslmode=verify-full` | the importer run by `just deploy staging` (migrations need a session connection) |
| Neon connection string | the Hyperdrive config, in Cloudflare | the same string, given once at creation | the Worker, through the `HYPERDRIVE` binding |
| Hyperdrive config id | `apps/web/wrangler.jsonc` (public, not a secret) | id printed by `wrangler hyperdrive create` | the Worker deployment |

Cloudflare needs no token in GitHub: Workers Builds authenticates through its GitHub App. The
Hyperdrive config keeps its own copy of the connection string: rotate it in both places.

## Re-creating the pieces

### Neon

1. Create the project `ohm-sweet-ohm` (free plan, region `eu-central-1`).
2. Copy the **direct** connection string with its query replaced by `?sslmode=verify-full` into
   a git-ignored `.env.staging` at the repository root (`DATABASE_URL=…`).
3. Fill the database once: `just deploy staging` from up-to-date `main` renders the schematics in
   Docker, applies the migrations and mirrors the catalogue (`scripts/deploy.sh catalogue staging`
   reads `DATABASE_URL` from `.env.staging`).

Scale to zero is always on: the compute suspends after 5 minutes without connection and wakes on
the next one. The free plan gives 100 CU-hours a month.

### Hyperdrive

Create the config once, from a shell where the string never reaches the history (read it from
`.env.staging`):

```bash
set -a; . ./.env.staging; set +a
pnpm -C apps/web exec wrangler hyperdrive create ohm-sweet-ohm-catalogue \
  --connection-string="$DATABASE_URL" --caching-disabled
```

Copy the printed `id` into `apps/web/wrangler.jsonc`, in the `hyperdrive` entry with the binding
`HYPERDRIVE` and in the `previews` block (previews do not inherit it). The same entry carries a `localConnectionString` for local development. The free
plan allows 100,000 queries a day; `pg` 8.16.3 or later is required (the repository has 8.23.1).

### Cloudflare Workers Builds

In the Cloudflare dashboard, Workers → the Worker `ohm-sweet-ohm-web` → Settings → Build:

| Setting | Value |
| --- | --- |
| Git repository | `benoit-bremaud/ohm-sweet-ohm` |
| Production branch | `main` |
| Root directory | `apps/web` |
| Build command | `pnpm build` |
| Deploy command | `npx wrangler deploy` |
| Preview command | `npx wrangler preview` |
| Non-production branch builds | enabled (preview per branch, URL commented on the PR) |

Workers Builds uses the `wrangler` version pinned in `apps/web/package.json`. The first build must
be created by connecting the repository from the dashboard; later changes to `wrangler.jsonc`
deploy themselves.

### Verify the site

```bash
curl -i https://ohm.benoitbremaud.fr/blocks/led-resistor-basic              # 200, block page
curl -i https://ohm.benoitbremaud.fr/blocks/led-resistor-basic/schematic.svg  # 200, image/svg+xml, ETag, sandboxed CSP
curl -i https://ohm.benoitbremaud.fr/                                        # 302 to /depannage/
sh scripts/check-live.sh                                                                          # the nightly liveness check
```

## Local CI

Every check runs on the machine (#68, skill `local-ci`): the local tiers are deterministic, need no
agent and cost no Actions minutes (the repository was private and billed until 2026-11-07).
`mise.toml` pins every tool (Node, pnpm, just, lefthook, gitleaks, typos, actionlint, zizmor, hadolint, trivy,
trufflehog, act) with checksums in `mise.lock`; docker, `gh`, `ssh-keygen` and `sonar-scanner`
stay system tools. The hooks run the tools through `mise x --`, so they work whether or not the
shell activates mise.

```bash
just setup     # once per clone: mise install, pnpm install --frozen-lockfile, just sync, lefthook install
just fast      # L0, pre-commit hook: gitleaks, eslint, prettier, markdownlint, typos, hadolint… on the staged files
just check     # L1, pre-push hook: lint + test + security + secrets, under 3 min
just gate      # L2, before every merge, on the pushed head: check + SonarQube, Trivy fs, render, attestation
just nightly   # L3, systemd user timer: liveness of the production site (`scripts/check-live.sh`), Trivy fs and TruffleHog fail; check and mise outdated --bump only warn
```

The nightly timer runs at 04:00 in a detached worktree of `origin/main` under
`~/.cache/nightly/ohm-sweet-ohm`, fetched, reset and cleaned each run, never the working checkout
(#71, agents-skills#427), and `notify-send`s a failure. A dead site (`/` not redirecting to `/depannage/`, or the LED block page or its schematic not answering 200, after one retry), Trivy and TruffleHog findings fail it;
`just check` and `mise outdated --bump` only warn. Install the units by copying them from
`origin/main` (a link would follow whatever branch the checkout is on), again after every change:

```bash
for f in ohm-sweet-ohm-nightly.service ohm-sweet-ohm-nightly-failed.service ohm-sweet-ohm-nightly.timer; do git show origin/main:scripts/systemd/$f > ~/.config/systemd/user/$f; done
systemctl --user daemon-reload
systemctl --user enable --now ohm-sweet-ohm-nightly.timer
```

`just test` measures test coverage (`pnpm test:coverage`, V8, floor 80 % for each package,
`main.ts` entry points excluded), documentation coverage (`pnpm doc:coverage`, share of exported
declarations with a doc block, floor 90 %) and runs the wiring tests of the local CI itself
(`scripts/test-local-ci.sh`, `scripts/test-attest.sh`) and the figure generator tests
(`scripts/test-figures.sh`: coverage floor 90 %, committed SVGs equal to the generated
ones) and the diagram test of the web site (each `troubleshooting/*/arbre-N.svg` carries the hash
of its Mermaid source and render settings; run `just trees` after changing a diagram). `just sonar` sends the analysis and the lcov
report to the shared SonarQube at `http://localhost:9000` and fails when the quality gate fails; it
uses the machine's global analysis token (`SONAR_TOKEN`, or `~/.config/sonarqube/analysis-token`).

`just security` runs Semgrep Community Edition with the registry rulesets `p/javascript`,
`p/typescript` and `p/nodejs` on the shipped code and the scripts (`.semgrepignore` lists the
exclusions; suppress a finding only with an inline `nosemgrep: <rule-id>` and the reason) and
`pnpm audit --audit-level high` on every dependency, dev ones included (Trivy skips pnpm dev
dependencies, so it is the only check that sees them); `just gate` adds Trivy fs on the lockfile. `check` and `gate` need
network access (registry rules, advisories, SonarQube) and Docker (Testcontainers, images).

The first merge after #68 cannot use `just merge`: the verifier reads `.github/allowed_signers` from
`origin/main`, which only has it once #68 is merged, so #68 itself merges with `gh pr merge` and the
recorded waiver; every later PR goes through `just merge`.

`just gate` ends with the attestation (agents-skills ADR-0003): a signed git note on
`refs/notes/gate` and the commit status `gate` on the pushed head, verified by `just merge <pr>`. Signing is SSH: `git config gpg.format ssh` and `user.signingkey` pointing at a
public key listed in `.github/allowed_signers`, with its private key in `ssh-agent`. A squash merge
creates a new `main` commit with no attestation: run `just gate` again on `main` before
`just deploy staging`; after the staging QA pass, `just attest staging` records it.

### Release

There is no production deploy step: the production Worker is deployed by Workers Builds from
`main`, and the catalogue is imported by `just deploy staging`. A signed release tag `vX.Y.Z`
(skill `release-tag`) on a `main` commit that carries both attestations marks the release and
deploys nothing by itself.

## Local image checks

The only Dockerfile left is `docker/renderer/Dockerfile`, which runs on the curator's machine and
serves no traffic. `just gate` runs the checks; one at a time:

```bash
just lint                                                    # Hadolint on the renderer Dockerfile, among the linters
trivy config --exit-code 1 --severity HIGH,CRITICAL --misconfig-scanners dockerfile --skip-dirs node_modules,build,dist,coverage,.wrangler .   # as in the gate
```
