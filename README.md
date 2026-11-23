# Ohm Sweet Ohm

A public API (and its demo web front-end) that helps electronics enthusiasts find
a **reusable circuit block** matching a precise need — and explore its variants,
from the simplest base circuits to more complex ones.

> Status: milestone M1 (first vertical slice) done, M2 (variant trees) next — tracked in the [GitHub Project](https://github.com/users/benoit-bremaud/projects/61).

## Documentation

- [Project framing](docs/FRAMING.md) — vision, decisions, deferred features.
- [Work plan](docs/WORKPLAN.md) — v1 milestones (vertical slices, 2-week cadence).
- [Project log](PROJECT_LOG.md) — chronological operational logbook.
- [Electronics troubleshooting guides](troubleshooting/README.md) — how to tell whether a component on a board is dead (French).

## Development

Requires [mise](https://mise.jdx.dev) and Docker; `mise.toml` pins Node 22, pnpm 10 and every
check tool (see `docs/deploy.md` § Local CI).

```bash
mise trust && mise install && mise x -- just setup   # once per clone: toolchain, pnpm install, Astro sync, git hooks (just itself comes from mise)
just check   # format, lint, typecheck, tests with coverage, Semgrep, audit, gitleaks (pre-push hook)
just gate    # the pre-merge gate: check + SonarQube, Trivy fs, catalogue render, attestation
```

Integration tests start a disposable PostgreSQL with Testcontainers, so Docker must be running.

Publish the catalogue to a database (Docker required for rendering):

```bash
just render
DATABASE_URL=postgres://user:password@localhost:5432/ohm pnpm catalogue:import
```

The import mirrors the `catalogue/` folder: it adds, updates and removes blocks so the database
matches it exactly, and refuses to run when no block is found.

Run the web front-end (Astro on Cloudflare Workers, ADR-0003). It runs in `workerd`, the
production runtime, and reads the catalogue straight from PostgreSQL through the `HYPERDRIVE`
binding (ADR-0005). Locally the binding points at the `localConnectionString` of
`apps/web/wrangler.jsonc` (`postgres://user:password@localhost:5432/ohm`); set
`CLOUDFLARE_HYPERDRIVE_LOCAL_CONNECTION_STRING_HYPERDRIVE` to use another database. Start a local
PostgreSQL there, import the catalogue into it, then start the dev server:

```bash
just render
DATABASE_URL=postgres://user:password@localhost:5432/ohm pnpm catalogue:import
pnpm -C apps/web dev
```

Then open `http://localhost:4321/blocks/led-resistor-basic`. A new import is visible within a few
seconds. `pnpm --filter @ohm-sweet-ohm/web build` produces the Worker in `apps/web/dist`;
deployment is configured in `apps/web/wrangler.jsonc`.

## Deployment

The site runs on Cloudflare Workers (web, one preview per branch) reading Neon (PostgreSQL)
through Hyperdrive; there is no API server and no Fly.io since ADR-0005. `just deploy staging`
imports the catalogue into Neon from an attested `main`, and `just nightly` checks that the
production site answers. No GitHub workflow is left. Setup, secrets, re-creation steps, the
local CI tiers and the container checks are in [docs/deploy.md](docs/deploy.md); the decision is
[ADR-0005](docs/architecture/decisions/0005-worker-reads-neon-through-hyperdrive.md).

## Licenses

- Code: [MIT](LICENSE).
- Schematics catalogue: [CC BY-SA 4.0](catalogue/LICENSE).
- Troubleshooting guides: [CC BY-SA 4.0](troubleshooting/LICENSE).
- Studies and course sheets: CC BY-SA 4.0 (the `studies/LICENSE` file arrives with #56, the course-sheet licence file with #58).
