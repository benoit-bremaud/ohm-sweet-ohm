# ADR-0004 — Staging hosting: API on Fly.io, PostgreSQL on Neon, web previews by Workers Builds

- Status: accepted
- Date: 2026-10-15
- Deciders: Benoît Bremaud
- Related: issue #19 (deployment), issue #24 (HSTS and `script-src` once the domain exists),
  [ADR-0003](0003-web-astro-cloudflare.md), the deployment view in
  [03-component.md](../diagrams/catalogue/03-component.md)

## Context and problem statement

Milestone M1 is done when the LED page is reachable on a Cloudflare Workers branch preview URL,
fed end to end by the catalogue. The web app runs on Workers (ADR-0003), but the API (Fastify
with a `pg` connection pool) cannot: it needs a container, and the catalogue needs a managed
PostgreSQL that the importer fills from CI on every merge. The staging tier is the disposable PR
preview for the web app; the API and the database have no per-branch preview, so they are one
long-lived staging deployment that every web preview talks to (allowed by the environment
convention when the infrastructure offers no automatic previews). The budget of a part-time solo
project is a few euros a month at most. Three choices follow: the container platform, the
database provider and the mechanism that builds the web previews.

Facts verified on 2026-10-15: a Fly.io account exists with `flyctl` logged in and two apps
already deployed from other projects; the Cloudflare account is logged in through `wrangler`;
Fly.io sells no free tier any more (usage billing, a `shared-cpu-1x` Machine costs about 2 to
4 USD a month when it runs, nothing for CPU while stopped); Render's free web services sleep
after 15 minutes and take up to a minute to wake; Cloudflare Containers need the Workers Paid
plan (5 USD a month) and a Durable Object Worker in front of the container; Fly Managed Postgres
starts at 38 USD a month; Supabase pauses free projects after 7 days without activity; Neon's
free plan gives 100 CU-hours a month and 1 GB per project, suspends the compute after 5 minutes
of inactivity and wakes it on the next connection.

## Decision 1 — API container platform

Options: **A** Fly.io Machine (Dockerfile deployed as is, `auto_stop` and `auto_start`, region
`cdg`); **B** Render free web service; **C** Cloudflare Containers. Railway was not scored: paid
like Fly, with neither account nor precedent. Scores 0 (blocking) to 5 (ideal); weights sum to
100, so the maximum is 500 points. Weights validated by the owner on 2026-10-15.

| # | Criterion | Weight | A — Fly.io | B — Render free | C — Cloudflare Containers |
| --- | --- | --- | --- | --- | --- |
| 1 | Runs Fastify from the Dockerfile as is | 20 | 5 — `fly deploy` reads the Dockerfile; precedent on two projects | 5 — native Docker | 3 — a Durable Object Worker and a container class to write |
| 2 | Staging cost | 15 | 4 — about 2 to 4 USD a month, CPU billed only while running | 5 — free (750 hours a month) | 3 — 5 USD a month, usage included |
| 3 | Demo always reachable (no hanging page) | 20 | 4 — a stopped Machine starts in about a second (measured on V-SEA) | 1 — up to a minute to wake after 15 idle minutes | 3 — wakes in seconds after sleeping |
| 4 | Owner preference, account and precedent | 15 | 5 — account, CLI logged in, two apps deployed | 2 — no account | 4 — Cloudflare account, no Containers precedent |
| 5 | Maturity, documentation | 10 | 5 — established platform | 4 — established, Docker secondary | 2 — generally available since 2025; no preview URL for Durable Object Workers |
| 6 | Simplicity of the CI deployment (KISS) | 10 | 4 — one `flyctl deploy` workflow with a deploy token | 4 — automatic deployment from GitHub | 3 — `wrangler deploy` pushes the image, plus the Worker |
| 7 | Fit with the `docker-hardening` rules (non-root, HEALTHCHECK, Trivy) | 10 | 5 — Fly checks on `/health`, non-root verifiable | 4 — fine | 3 — Dockerfile honoured, HEALTHCHECK ignored |

| Criterion (weight) | A | B | C |
| --- | --- | --- | --- |
| 1 (20) | 100 | 100 | 60 |
| 2 (15) | 60 | 75 | 45 |
| 3 (20) | 80 | 20 | 60 |
| 4 (15) | 75 | 30 | 60 |
| 5 (10) | 50 | 40 | 20 |
| 6 (10) | 40 | 40 | 30 |
| 7 (10) | 50 | 40 | 30 |
| **Total / 500** | **455** | **345** | **305** |

Sensitivity: doubling the cost weight (15 to 30) and cutting reachability (20 to 5) gives A 405
against B 355; doubling the owner-preference weight (15 to 30, maturity to 0) gives A 460 against
C 330. A holds in both. Estimate: the real monthly Fly cost (2 to 4 USD) is read on the first
invoice and recorded in `PROJECT_LOG.md`.

**Chosen: A, Fly.io, 455 points.** C is the all-Cloudflare option, but it wraps the API in a
Durable Object it does not need and trades maturity for it; A deploys the Dockerfile unchanged on
an account already in use. **Fallback: C (305)** — a design change (wrapper Worker), not a
drop-in.

## Decision 2 — Managed PostgreSQL

Options: **A** Neon free plan (eu-central-1, Frankfurt); **B** Supabase free plan; **C** Fly
Postgres, unmanaged (a Machine and a volume on the same account). Fly Managed Postgres was
eliminated before scoring: 38 USD a month is blocking (0) on the cost criterion.

| # | Criterion | Weight | A — Neon | B — Supabase | C — Fly Postgres unmanaged |
| --- | --- | --- | --- | --- | --- |
| 1 | Staging cost | 20 | 5 — free | 5 — free | 3 — about 2 to 3 USD a month, Machine always on plus a volume |
| 2 | Demo reliability (no pause, no expiry) | 25 | 4 — wakes on connection; 100 CU-hours a month suffice while the API stops when idle (estimate) | 1 — paused after 7 idle days, restored by hand | 3 — single node, no high availability, unsupported by Fly |
| 3 | Fit with `pg`, Kysely migrations and TLS | 15 | 5 — `sslmode=verify-full` in the URL, nothing to change | 4 — migrations must use the session port, not the transaction pooler | 5 — Fly private network, plain `pg` |
| 4 | Operations burden (backups, upgrades) | 15 | 5 — managed | 4 — managed | 2 — backups and upgrades on the owner |
| 5 | Latency to the API in `cdg` | 10 | 4 — Frankfurt, about 10 to 15 ms (estimate) | 4 — eu-central | 5 — same region, private network |
| 6 | Future fit (database per PR, growth) | 10 | 5 — Neon branches per PR possible from M2 | 3 — no branches | 2 — none |
| 7 | Existing account | 5 | 2 — to create | 2 — to create | 5 — Fly account |

| Criterion (weight) | A | B | C |
| --- | --- | --- | --- |
| 1 (20) | 100 | 100 | 60 |
| 2 (25) | 100 | 25 | 75 |
| 3 (15) | 75 | 60 | 75 |
| 4 (15) | 75 | 60 | 30 |
| 5 (10) | 40 | 40 | 50 |
| 6 (10) | 50 | 30 | 20 |
| 7 (5) | 10 | 10 | 25 |
| **Total / 500** | **450** | **325** | **335** |

Sensitivity: raising the existing-account weight to 25 (reliability 15, cost 10) gives A 400
against C 375, so that weight is the debatable one and A still holds. Estimate to verify: Neon's
100 CU-hours a month (0.25 CU minimum while active) hold as long as the API stops when idle and
so stops checking the catalogue version; the consumption is read on the Neon dashboard after the
first week and recorded in `PROJECT_LOG.md`.

**Chosen: A, Neon, 450 points.** C stays inside the Fly account but leaves the backups to the
owner and runs all the time; A is managed, free, and opens a database per PR later.
**Fallback: C (335)** — a drop-in (same `DATABASE_URL`), about 3 USD a month.

## Decision 3 — Web preview mechanism

Options: **A** Workers Builds (Cloudflare's GitHub App, build and preview commands set in the
dashboard); **B** GitHub Actions running `wrangler versions upload` and commenting the URL.

| # | Criterion | Weight | A — Workers Builds | B — GitHub Actions |
| --- | --- | --- | --- | --- |
| 1 | Preview comment on the pull request | 30 | 5 — native, one alias per branch | 4 — documented workflow plus `gh pr comment` |
| 2 | Configuration versioned in git | 25 | 2 — root directory and commands live in the dashboard | 5 — everything in the workflow |
| 3 | Secrets to hold in GitHub | 20 | 5 — none | 2 — Cloudflare API token and account id |
| 4 | KISS | 25 | 4 — connect the repository once | 3 — workflow plus comment upsert |

| Criterion (weight) | A | B |
| --- | --- | --- |
| 1 (30) | 150 | 120 |
| 2 (25) | 50 | 125 |
| 3 (20) | 100 | 40 |
| 4 (25) | 100 | 75 |
| **Total / 500** | **400** | **360** |

**Chosen: A, Workers Builds, 400 points**, as ADR-0003 already named it: B wins on
reproducibility, A on the absence of secrets and the native comment. **Fallback: B (360)**, a
drop-in. The dashboard settings are recorded in the deployment README so they can be re-entered.

## Decision outcome

- `apps/api/Dockerfile` (non-root, HEALTHCHECK on `/health`, pinned base, Hadolint and Trivy in
  CI per the container rules) deployed to the Fly app `ohm-sweet-ohm-api` in `cdg` by a GitHub
  Actions workflow on every merge to `main`, with `auto_stop_machines` so an idle staging costs
  nothing in CPU. Secrets: `FLY_API_TOKEN` in GitHub, `DATABASE_URL` in Fly.
- One Neon project `ohm-sweet-ohm`, free plan, Frankfurt; its direct (unpooled) connection string
  is the `DATABASE_URL` of both the API (Fly secret) and the importer (GitHub secret). The
  catalogue is imported from CI on every merge to `main` that touches the catalogue, the renderer
  or the importer's code, after the schematics are rendered in Docker.
- `apps/web` is built and deployed by Workers Builds: production from `main`, a preview per
  branch, the URL commented on the pull request. `API_URL` in `wrangler.jsonc` points at the Fly
  app for both.

### Consequences

- Good: the whole M1 slice runs on free or near-free tiers; the only recurring cost is the Fly
  Machine while it serves requests.
- Good: every PR gets a web preview without any secret in GitHub; the API and the database are
  shared by all previews, which matches read-only content.
- Bad: three providers to know (Cloudflare, Fly, Neon) and two consoles outside git (Workers
  Builds settings, Neon project).
- Bad: the first request after an idle period pays two cold starts (Fly Machine, Neon compute);
  acceptable for staging, to measure before production.
- Issue #24 (HSTS, `script-src 'none'`) can proceed on the `workers.dev` host.

### Revisit when

A production domain and real traffic arrive (Neon compute hours, Fly always-on Machine, a
production Worker environment), or when M2 needs a database per PR (Neon branches).
