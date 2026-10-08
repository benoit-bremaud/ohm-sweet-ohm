# Project log — Ohm Sweet Ohm

Chronological operational logbook. Release history lives in `CHANGELOG.md` (from v1.0.0).

## 2026-10-08

- **Project framing** — brainstorming sessions produced [docs/FRAMING.md](docs/FRAMING.md)
  and [docs/WORKPLAN.md](docs/WORKPLAN.md).
  - **Decisions**:
    - `Curated catalogue of reusable circuit blocks` — quality and licensing control over volume; aggregation and community contributions deferred.
    - `Base circuits + variant trees` — users start from a well-known base circuit and explore variants (single parent per variant); browsing by key component deferred to v2.
    - `Structured filters first` — natural language search deferred to v2, built as a translation into the same filters.
    - `TypeScript + Fastify + PostgreSQL, Next.js front` — shared types, range types for specs, pgvector available for v2; Python rejected to keep a single language.
    - `Vertical slices` — layer-by-layer delivery rejected: nothing visible before week 9 is an abandonment risk for a part-time solo project.
    - `Single pnpm monorepo, catalogue in-repo` — one source of truth for Zod schemas; split repos rejected as friction without contributors.
- **Repository initialised** — initial commit made directly on `main` (no branch possible on an empty repository): README, MIT license, `.gitignore`, framing documents, this log.
