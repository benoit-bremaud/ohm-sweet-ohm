# Deployment — staging

How the M1 slice is deployed (ADR-0004, deployment view in
[03-component.md](architecture/diagrams/catalogue/03-component.md)). Staging is the disposable
preview of a pull request for the web app; the API and the database are one long-lived staging
deployment shared by every preview. Secrets never enter the repository: they live in GitHub
Actions secrets, Fly secrets and the Neon console.

| Part | Where | Deployed by | URL |
| --- | --- | --- | --- |
| `apps/web` | Cloudflare Workers | Workers Builds (`main` → production, other branches → preview) | `https://ohm-sweet-ohm-web.<account>.workers.dev`, preview URL commented on the PR |
| `apps/api` | Fly.io, app `ohm-sweet-ohm-api`, region `cdg` | `.github/workflows/deploy-api.yml` on every push to `main` | `https://ohm-sweet-ohm-api.fly.dev` |
| PostgreSQL | Neon, project `ohm-sweet-ohm`, free plan, `eu-central-1` | `.github/workflows/catalogue.yml` imports the catalogue on every push to `main` | — |

## Secrets and variables

| Name | Where | Value | Used by |
| --- | --- | --- | --- |
| `DATABASE_URL` | GitHub Actions secret | Neon **direct** connection string (no `-pooler`), with `?sslmode=verify-full` | the importer in CI (migrations need a session connection) |
| `DATABASE_URL` | Fly secret of `ohm-sweet-ohm-api` | the same string | the API |
| `FLY_API_TOKEN` | GitHub Actions secret | deploy token scoped to the app | `deploy-api.yml` |
| `API_URL` | `apps/web/wrangler.jsonc` (public) | `https://ohm-sweet-ohm-api.fly.dev` | the Worker, production and previews |

Cloudflare needs no token in GitHub: Workers Builds authenticates through its GitHub App.

## Re-creating the pieces

### Neon

1. Create the project `ohm-sweet-ohm` (free plan, region `eu-central-1`).
2. Copy the **direct** connection string, append `?sslmode=verify-full`, and store it as the
   `DATABASE_URL` secret in GitHub (Settings → Secrets and variables → Actions) and in Fly.
3. Fill the database once: run the `Catalogue` workflow by hand (`workflow_dispatch`); it
   renders the schematics in Docker, applies the migrations and mirrors the catalogue.

Scale to zero is always on: the compute suspends after 5 minutes without connection and wakes on
the next one. The free plan gives 100 CU-hours a month; the API stops when idle, so it only
checks the catalogue version while it serves requests.

### Fly.io

```bash
flyctl apps create ohm-sweet-ohm-api --org personal
flyctl secrets set DATABASE_URL='<neon direct connection string>' --app ohm-sweet-ohm-api
flyctl tokens create deploy --app ohm-sweet-ohm-api --expiry 8760h   # → FLY_API_TOKEN in GitHub
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
deploy themselves.

## Local image checks

```bash
make lint-docker          # Hadolint, pinned image
make scan-docker-config   # Trivy, Dockerfile misconfigurations
make build-api            # docker build -f apps/api/Dockerfile
make scan-docker-image    # Trivy, HIGH and CRITICAL with a fix
docker run --rm -p 3000:3000 -e DATABASE_URL=postgres://user:password@host.docker.internal:5432/ohm ohm-sweet-ohm-api
```
