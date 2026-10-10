# Ohm Sweet Ohm

A public API (and its demo web front-end) that helps electronics enthusiasts find
a **reusable circuit block** matching a precise need — and explore its variants,
from the simplest base circuits to more complex ones.

> Status: milestone M0 (foundations & modelling) in progress — tracked in the [GitHub Project](https://github.com/users/benoit-bremaud/projects/61).

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

## Licenses

- Code: [MIT](LICENSE).
- Schematics catalogue: [CC BY-SA 4.0](catalogue/LICENSE).
