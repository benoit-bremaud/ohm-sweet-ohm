# Ohm Sweet Ohm

A public API (and its demo web front-end) that helps electronics enthusiasts find
a **reusable circuit block** matching a precise need — and explore its variants,
from the simplest base circuits to more complex ones.

> Status: milestone M1 (first vertical slice) in progress — tracked in the [GitHub Project](https://github.com/users/benoit-bremaud/projects/61).

## Documentation

- [Project framing](docs/FRAMING.md) — vision, decisions, deferred features.
- [Work plan](docs/WORKPLAN.md) — v1 milestones (vertical slices, 2-week cadence).
- [Project log](PROJECT_LOG.md) — chronological operational logbook.

## Development

Requires Node.js 22 (see `.nvmrc`) and pnpm 10.

```bash
pnpm install
pnpm check   # format, lint (TypeScript + Markdown), typecheck, tests
```

Integration tests start a disposable PostgreSQL with Testcontainers, so Docker must be running.

Publish the catalogue to a database (Docker required for rendering):

```bash
pnpm catalogue:render
DATABASE_URL=postgres://user:password@localhost:5432/ohm pnpm catalogue:import
```

The import mirrors the `catalogue/` folder: it adds, updates and removes blocks so the database
matches it exactly, and refuses to run when no block is found.

Serve the catalogue (the importer applies the migrations; the API only reads):

```bash
DATABASE_URL=postgres://user:password@localhost:5432/ohm pnpm --filter @ohm-sweet-ohm/api start
```

`PORT` (default 3000) and `HOST` (default `0.0.0.0`) are optional. The interactive API
documentation is served at `/docs`. A new import is visible within 5 seconds; if the database
becomes unreachable, the API keeps serving the catalogue already in memory.

## Licenses

- Code: [MIT](LICENSE).
- Schematics catalogue: [CC BY-SA 4.0](catalogue/LICENSE).
