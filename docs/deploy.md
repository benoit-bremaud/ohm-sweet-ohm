# Deployment — staging

How the M1 slice is deployed (ADR-0004, deployment view in
[03-component.md](architecture/diagrams/catalogue/03-component.md)). Staging is the disposable
preview of a pull request for the web app; the API and the database are one long-lived deployment
shared by every preview. Since #68 every check runs locally (§ Local CI) and GitHub Actions keeps
one workflow, `prod.yml`, triggered by a signed stable tag; staging is deployed from the curator's
machine with `just deploy staging`. Secrets never enter the repository: they live in Fly secrets,
the git-ignored `.env.staging` and one GitHub repository secret.

| Part | Where | Deployed by | URL |
| --- | --- | --- | --- |
| `apps/web` | Cloudflare Workers | Workers Builds (`main` → production, other branches → preview) | `https://ohm-sweet-ohm-web.<account>.workers.dev`, preview URL commented on the PR |
| `apps/api` | Fly.io, app `ohm-sweet-ohm-api`, region `cdg` | `just deploy staging` from up-to-date `main` after a green `just gate`; `prod.yml` on a signed `vX.Y.Z` tag (`just deploy prod <tag>` when Actions cannot run) | `https://ohm-sweet-ohm-api.fly.dev` |
| PostgreSQL | Neon, project `ohm-sweet-ohm`, free plan, `eu-central-1` | `just deploy staging`: `just render`, then `pnpm catalogue:import` with `DATABASE_URL` from `.env.staging` | — |

The API has one Fly app and one Neon project: staging and production share them until a second
app exists (derogation recorded in `PROJECT_LOG.md`, 2026-11-07); a stable tag redeploys the same
app from the tagged commit. Migrations run in the importer only; `just deploy staging` imports the
catalogue before it deploys the API, so a migration is applied before the API that needs it starts.

## Secrets and variables

| Name | Where | Value | Used by |
| --- | --- | --- | --- |
| `DATABASE_URL` | `.env.staging` at the repository root, git-ignored | Neon **direct** connection string (no `-pooler`), with `?sslmode=verify-full` | the importer run by `just deploy staging` (migrations need a session connection) |
| `DATABASE_URL` | Fly secret of `ohm-sweet-ohm-api` | the same string | the API |
| `FLY_API_TOKEN` | GitHub repository secret | deploy token scoped to the app, with an expiry | `prod.yml`; the local deploys use the `flyctl` session |
| `API_URL` | `apps/web/wrangler.jsonc` (public) | `https://ohm-sweet-ohm-api.fly.dev` | the Worker, production and previews |

Cloudflare needs no token in GitHub: Workers Builds authenticates through its GitHub App.

## Re-creating the pieces

### Neon

1. Create the project `ohm-sweet-ohm` (free plan, region `eu-central-1`).
2. Copy the **direct** connection string with its query replaced by `?sslmode=verify-full` into
   a git-ignored `.env.staging` at the repository root (`DATABASE_URL=…`), then feed the secrets
   from that file so the value never goes through the shell history or the terminal:

   ```bash
   flyctl secrets import --app ohm-sweet-ohm-api < .env.staging
   ```

   With the Neon CLI signed in, `neonctl connection-string --project-id <id>` prints the string
   and can be piped the same way.
3. Fill the database once: `just deploy staging` from up-to-date `main` renders the schematics in
   Docker, applies the migrations and mirrors the catalogue (`scripts/deploy.sh catalogue staging`
   reads `DATABASE_URL` from `.env.staging`), then deploys the API.

Scale to zero is always on: the compute suspends after 5 minutes without connection and wakes on
the next one. The free plan gives 100 CU-hours a month; the API stops when idle, so it only
checks the catalogue version while it serves requests.

### Fly.io

```bash
flyctl apps create ohm-sweet-ohm-api --org personal
flyctl secrets import --app ohm-sweet-ohm-api < .env.staging          # DATABASE_URL, see Neon
flyctl tokens create deploy --app ohm-sweet-ohm-api --expiry 8760h --json \
  | jq -r .token | gh secret set FLY_API_TOKEN                        # never printed
flyctl deploy --remote-only --ha=false --config apps/api/fly.toml     # from the repository root
```

`--ha=false` keeps one Machine: without it Fly creates two for high availability, which staging
does not need.

The Machine (`shared-cpu-1x`, 256 MB) stops a few minutes after the last request and starts on
the next one (`auto_stop_machines`, `min_machines_running = 0`): an idle staging costs no compute,
and only the root file system is billed. Check the deployment:

```bash
curl -i https://ohm-sweet-ohm-api.fly.dev/health
curl -s https://ohm-sweet-ohm-api.fly.dev/blocks/led-resistor-basic | head -c 300
flyctl status --app ohm-sweet-ohm-api
```

Verify the process runs unprivileged (Fly's init is PID 1, so look for the Node process):

```bash
flyctl ssh console --app ohm-sweet-ohm-api -C "sh -c 'for p in /proc/[0-9]*; do grep -qa \"[d]ist/main.js\" \$p/cmdline && grep -E \"^(Uid|CapEff|NoNewPrivs)\" \$p/status; done'"
```

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
deploy themselves. Branch previews read their variables from the `previews` block of
`wrangler.jsonc`, not from the top-level `vars`, so `API_URL` is declared in both.

## Local CI

Every check runs on the machine (#68, skill `local-ci`): GitHub Actions bills the minutes of a
private repository, and the local tiers are deterministic and need no agent. `mise.toml` pins every
tool (Node, pnpm, just, lefthook, gitleaks, typos, actionlint, zizmor, hadolint, trivy, syft,
trufflehog, act) with checksums in `mise.lock`; docker, flyctl and `sonar-scanner`
stay system tools. The hooks run the tools through `mise x --`, so they work whether or not the
shell activates mise.

```bash
just setup     # once per clone: mise install, pnpm install --frozen-lockfile, lefthook install
just fast      # L0, pre-commit hook: gitleaks, eslint, prettier, markdownlint, typos, hadolint… on the staged files
just check     # L1, pre-push hook: lint + test + security + secrets, under 3 min
just gate      # L2, before every merge, on the pushed head: check + SonarQube, Trivy, API image smoke, SBOM, render, attestation
just nightly   # L3, systemd user timer: check + TruffleHog + mise outdated
```

`just test` measures test coverage (`pnpm test:coverage`, V8, floor 80 % for each package,
`main.ts` entry points excluded), documentation coverage (`pnpm doc:coverage`, share of exported
declarations with a doc block, floor 90 %) and runs the wiring tests of the local CI itself
(`scripts/test-local-ci.sh`, `scripts/test-attest.sh`). `just sonar` sends the analysis and the lcov
report to the shared SonarQube at `http://localhost:9000` and fails when the quality gate fails; it
uses the machine's global analysis token (`SONAR_TOKEN`, or `~/.config/sonarqube/analysis-token`).

`just security` runs Semgrep Community Edition with the registry rulesets `p/javascript`,
`p/typescript` and `p/nodejs` on the shipped code and the scripts (`.semgrepignore` lists the
exclusions; suppress a finding only with an inline `nosemgrep: <rule-id>` and the reason) and
`pnpm audit --prod --audit-level high`; `just gate` adds Trivy on the lockfile. `check` and `gate` need
network access (registry rules, advisories, SonarQube) and Docker (Testcontainers, images).

`just gate` ends with the attestation (agents-skills ADR-0003): a signed git note on
`refs/notes/gate` and the commit status `gate` on the pushed head, verified by `just merge <pr>`
and by `prod.yml`. Signing is SSH: `git config gpg.format ssh` and `user.signingkey` pointing at a
public key listed in `.github/allowed_signers`, with its private key in `ssh-agent`. A squash merge
creates a new `main` commit with no attestation: run `just gate` again on `main` before
`just deploy staging`; after the staging QA pass, `just attest staging` records it, which the
production tag requires.

### Release

A stable tag `vX.Y.Z`, SSH-signed by a key of `.github/allowed_signers`, on a `main` commit that
carries both attestations, triggers `prod.yml`: it classifies the tag, re-fetches `main`, runs the
`scripts/attest.sh release` of `main` (never the tagged one), then `scripts/deploy.sh api prod`
with the `FLY_API_TOKEN` repository secret. A pre-release tag (`-alpha.N`, `-beta.N`, `-rc.N`) is
classified and deploys nothing; any other tag fails the run. When Actions cannot run,
`just deploy prod <tag>` from up-to-date `main` performs the same checks and the same deploy.

## Local image checks

`just gate` runs them all; one at a time:

```bash
just lint                                                    # Hadolint on both Dockerfiles, among the linters
trivy config --misconfig-scanners dockerfile .               # Dockerfile misconfigurations
docker build -f apps/api/Dockerfile -t ohm-sweet-ohm-api:gate .
just smoke                                                   # the image starts and its health check passes
trivy image --ignore-unfixed --severity HIGH,CRITICAL ohm-sweet-ohm-api:gate
docker run --rm -p 3000:3000 --env-file .env.staging ohm-sweet-ohm-api:gate   # against the staging database
```
