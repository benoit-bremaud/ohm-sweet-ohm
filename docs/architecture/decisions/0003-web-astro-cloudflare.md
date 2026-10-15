# ADR-0003 — Web front-end: Astro rendered on Cloudflare Workers

- Status: accepted
- Date: 2026-10-15
- Deciders: Benoît Bremaud
- Related: issue #18 (web page), issue #19 (deployment), UC3 in
  [01-use-case.md](../diagrams/catalogue/01-use-case.md),
  [03-component.md](../diagrams/catalogue/03-component.md),
  [06-sequence-view-block-page.md](../diagrams/catalogue/06-sequence-view-block-page.md)
- Supersedes: the "Next.js, front on Vercel" rows of the framing (2026-10-08), which were never
  compared with an alternative.

## Context and problem statement

The web front-end shows one indexable page per block (M1), then the base circuits and their
variants (M2), a search page (M3) and a value calculator (M4). Every page is read-only content
fed by the API; the calculator is the only interactive part planned. The owner prefers hosting on
Cloudflare, where an account already exists. The framing had written "Next.js on Vercel" as the
default that comes with Next.js, with no decision record. Which framework and hosting should the
front-end use?

## Considered options

- **A. Next.js 16 on Cloudflare Workers** through the OpenNext adapter (`@opennextjs/cloudflare`
  1.20): App Router supported, Node runtime required, Node middleware not supported yet; Worker
  size limit 3 MiB compressed on the free plan.
- **B. Next.js 16 on Vercel**: the framing's choice; native, zero configuration, PR previews
  built in; the Hobby plan forbids commercial use.
- **C. Astro 7 on Cloudflare Workers** through the official adapter (`@astrojs/cloudflare` 14):
  server rendering with no client JavaScript by default, React islands when a page needs
  interactivity, development server running in `workerd` like production.

## Decision matrix (MCDA, weights validated by the owner on 2026-10-15)

Scores 0 (blocking) to 5 (ideal); weights sum to 100, so the maximum is 500 points.

| # | Criterion | Weight | A — Next + Cloudflare | B — Next + Vercel | C — Astro + Cloudflare |
| --- | --- | --- | --- | --- | --- |
| 1 | Fit to the need: content pages, SEO, one interactive island | 20 | 3 — works, but most of the Next model stays unused | 3 — same | 5 — built for content sites, zero JS by default, React island for the calculator |
| 2 | Native Cloudflare (owner preference) | 15 | 3 — runs there through a third-party adapter | 0 — not Cloudflare | 5 — official adapter, dev runs in `workerd` |
| 3 | Maintenance risk on upgrades | 15 | 2 — the adapter follows Next; Node middleware unsupported | 5 — native, maintained by Next's publisher | 4 — official adapter versioned with Astro; breaking changes across majors |
| 4 | Free-tier limits and cost | 10 | 3 — 3 MiB compressed Worker limit, Next bundles are often close (estimate) | 2 — Hobby plan forbids commercial use | 5 — light Worker, far below the limit (estimate) |
| 5 | PR previews and deployment | 10 | 3 — Workers Builds plus OpenNext and wrangler configuration | 5 — nothing to configure | 4 — Workers Builds, `astro build && wrangler deploy` |
| 6 | Ecosystem, maturity, documentation | 10 | 3 — Next mature, adapter less so | 5 — the market reference | 4 — mature, well documented, smaller ecosystem |
| 7 | Portfolio and market value | 10 | 5 — Next.js in high demand | 5 — same | 3 — appreciated, less demanded |
| 8 | Front performance (JS shipped, response time) | 5 | 3 — React runtime shipped, adaptation layer (estimate) | 4 — React runtime shipped | 5 — plain HTML, JS only for islands |
| 9 | Cost of changing the plan | 5 | 4 — keep Next, change the host | 5 — none | 3 — this ADR, framing, work plan and issue #18 updated |

| Criterion (weight) | A | B | C |
| --- | --- | --- | --- |
| 1 (20) | 60 | 60 | 100 |
| 2 (15) | 45 | 0 | 75 |
| 3 (15) | 30 | 75 | 60 |
| 4 (10) | 30 | 20 | 50 |
| 5 (10) | 30 | 50 | 40 |
| 6 (10) | 30 | 50 | 40 |
| 7 (10) | 50 | 50 | 30 |
| 8 (5) | 15 | 20 | 25 |
| 9 (5) | 20 | 25 | 15 |
| **Total / 500** | **310** | **350** | **435** |

Sensitivity: doubling the portfolio weight (criterion 7 to 20, criterion 1 to 10) keeps C first
(405 against 330 and 370). B beats A: keeping Next.js is safer on Vercel than through an adapter.
Estimates: the Worker sizes (criterion 4) and the performance of A (criterion 8) were not
measured; the size of the Astro Worker is measured at the first build of `apps/web` and
recorded in `PROJECT_LOG.md`.

## Decision outcome

Chosen option: **C, Astro on Cloudflare Workers**, with 435 points out of 500.

- `apps/web` is an Astro project with `output: 'server'` (every page reflects an import within
  the API's 5 s freshness) and the Cloudflare adapter; the production branch and branch previews
  are deployed by Cloudflare Workers Builds (issue #19).
- The page reads the API over HTTP and validates the response with the shared
  `blockResponseSchema` (Zod at the boundary only). The web app depends on `packages/schemas`
  and never on `packages/db` or `packages/domain`.
- Schematics are shown with `<img src>` pointing at the API, never inlined, so the inert-SVG
  decision of issue #17 holds in the browser.
- No UI framework in M1: the first React island arrives with the calculator (M4).
- Page security: Astro's `security.csp` generates the Content-Security-Policy with hashes for
  its own inline styles (an own matrix scored it 500 against 200 for a hand-written header and
  270 for none); the remaining headers come from a small middleware.
- Component tests use Astro's Container API in a Vitest `node` project. The API is experimental,
  accepted because versions are pinned exactly and Dependabot plus CI would catch a break (an
  own matrix scored it 395 against 330 for pure-function tests only and 265 for HTTP tests
  through `wrangler dev`).

### Consequences

- Good: HTML without client JavaScript on every content page; small Worker; the development
  runtime is the production runtime.
- Good: the owner's hosting preference is met with an official adapter; no third-party adapter to
  follow.
- Bad: Next.js leaves the stack, which weighs on the portfolio criterion.
- Bad: the API (Fastify + PostgreSQL) cannot run on a Worker; its hosting is a separate decision
  of issue #19 whatever the front-end.
- The framing, the work plan and issue #18 are updated with this ADR.

### Revisit when

Most pages need client-side interactivity (then Next.js or a full React app may fit better), or
the Cloudflare free plan's limits are reached.
