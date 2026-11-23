# ADR-0005 — The web Worker reads Neon through Hyperdrive, Fly.io and the API are dropped

- Status: accepted
- Date: 2026-11-23
- Deciders: Benoît Bremaud
- Supersedes: [ADR-0004](0004-staging-hosting.md) for the API hosting (decision 1); Neon (decision 2)
  and Workers Builds (decision 3) are kept
- Amends: [ADR-0003](0003-web-astro-cloudflare.md) (the web app depended on `packages/schemas`
  only and showed schematics from the API)
- Related: issue #111 (public site down), [ADR-0003](0003-web-astro-cloudflare.md), the
  deployment view in [03-component.md](../diagrams/catalogue/03-component.md)

## Context and problem statement

The public site went down: the Fly.io app `ohm-sweet-ohm-api` no longer exists (it is absent from
the owner's only Fly organisation; the cause is unknown), so every block page answered 502. Fly.io
sells no free tier, so recreating the app also keeps a recurring cost. The Neon project
`ohm-sweet-ohm` still exists and holds the catalogue. The question is how to restore the site at
the lowest cost and delay, with the fewest providers.

Facts: the web Worker runs on Cloudflare (`ohm-sweet-ohm-web`, Workers Builds from `main`);
Cloudflare Hyperdrive is free on the Workers free plan (100,000 queries a day) and lets a Worker
reach a PostgreSQL database with `pg` 8.16.3 or later (the repository has 8.23.1).

## Decision 1 — Where the catalogue is served from

Options: **A** recreate the Fly app and keep the Fastify API; **B** Render free web service;
**C** port the read path to the Worker, which reads Neon through Hyperdrive; **D** Cloudflare
Containers. Scores 0 to 5; weights sum to 100, maximum 500. Weights validated by the owner on
2026-11-23.

| Criterion (weight) | A — Fly.io | B — Render free | C — Worker port | D — Containers |
| --- | --- | --- | --- | --- |
| Cost a month (35) | 3 | 5 | 5 | 2 |
| Effort and delay (25) | 5 | 4 | 1 | 3 |
| Reliability, cold start (20) | 4 | 1 | 5 | 4 |
| Fewer providers (20) | 3 | 2 | 5 | 4 |
| **Total / 500** | **370** | **335** | **400** | **305** |

Reasons: A costs a few euros a month and keeps three providers; B sleeps after 15 idle minutes;
D needs the 5 USD Workers Paid plan; C costs nothing and removes a provider, at the price of the
port.

Sensitivity: with effort 40, cost 25, reliability 20 and providers 15, A wins 400 against 340 for
C. The ranking depends on how much the owner values delay over cost; the owner kept the cost
weight.

**Chosen: C, 400 points.** Fallback: A (370), a drop-in of the previous design.

## Decision 2 — Architecture of the port

Options: **A** a separate Hono API Worker; **B** the web Worker reads Neon directly; **C** B plus
a public JSON route. Criteria: effort 30, public JSON API and OpenAPI 20, fewer moving parts 25,
reuse of existing tests 25.

| Criterion (weight) | A — Hono API Worker | B — Web reads Neon | C — B + JSON route |
| --- | --- | --- | --- |
| Effort (30) | 2 | 4 | 3 |
| Public JSON API, OpenAPI (20) | 5 | 1 | 3 |
| Fewer moving parts (25) | 3 | 5 | 4 |
| Reuse of tests (25) | 4 | 3 | 3 |
| **Total / 500** | **335** | **340** | **325** |

Sensitivity: with the API weight at 30 (effort 20), A wins.

**Chosen: B, 340 points.** The margin is small; the public API is out of the current milestone.

## Decision outcome

- `apps/api`, `.github/workflows/prod.yml`, the Fly app configuration and the API image are
  removed. `scripts/deploy.sh` keeps `catalogue staging` only; `just deploy staging` verifies the
  gate attestation, renders the schematics and imports the catalogue into Neon.
- The Worker reads the catalogue through the `HYPERDRIVE` binding (`apps/web/src/lib/catalogue-runtime.ts`):
  one connection per read, closed after it; an isolate-wide cache reloads the catalogue only when
  the catalogue version changes, checked at most every 5 seconds.
- The schematic is served by the Worker itself, same origin
  (`/blocks/{slug}/schematic.svg`: sandboxed CSP, `nosniff`, content-hash ETag, 304).
- `/` redirects (302) to `/depannage/` until the home page of the redesign (#161).
- `just nightly` runs `scripts/check-live.sh`: it fetches `/` (a 302 to `/depannage/`), the LED
  block page and its schematic on the production Worker and fails after one retry when one of
  them answers anything else (the pages and the SVG must answer 200).
- The Hyperdrive query cache is disabled (pending: the owner runs
  `wrangler hyperdrive update <id> --caching-disabled true` on the existing config): the version check and the catalogue reload are separate
  queries, and a cached reload could be stored under a fresh version; the isolate cache already
  spares the database.
- Workers Builds deploys the Worker on the merge, before the import: a migration ships
  expand-first and is imported with `just deploy staging` before the PR that reads it merges.
- Staging and production are the same Worker and the same Neon project.

### Consequences

- Good: no Fly.io, no container to run or scan, no GitHub workflow; free plan; one fewer provider.
- Good: the nightly now detects an outage the day it happens.
- Bad: no public JSON API and no `/docs` any more; the "third-party client" actor of the use-case
  diagram has no entry point until an API route is added.
- Bad: the Workers free plan limits CPU time per request; the catalogue reload must stay small.
- Bad: the importer and the Worker share the Neon credential until a read-only role exists.

### Revisit when

A public JSON API is wanted again (decision 2, option C), the free-plan CPU limit is hit, or the
Hyperdrive daily quota is approached.
