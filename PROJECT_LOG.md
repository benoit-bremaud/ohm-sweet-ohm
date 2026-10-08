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
- **M0 tracking set up on GitHub** — milestones M0–M5, `type:*` and `area:*` labels, M0 issues #1–#6. Order chosen: UML first (#1, #2), then tooling and CI (#3, #4), then the `meta.yaml` schema (#5) and the `kicad-cli` spike (#6). GitHub Project [Ohm Sweet Ohm (#61)](https://github.com/users/benoit-bremaud/projects/61) created and linked to the repository, holding issues #1–#6 and the PRs.
- **Use-case diagram** (branch `docs/1-use-case-diagram`, issue #1) — `docs/architecture/diagrams/catalogue/01-use-case.md`: six v1 use cases with Cockburn specifications, four v2 use cases shown dashed.
  - **Decisions**:
    - `Third-party developer generalizes Electronics enthusiast` — same goals through another channel; web and API are channels, not actors.
    - `Declaring a variant is publishing a block with a parent` — a separate use case would duplicate the publication flow.
    - `Fully object-oriented domain` — domain concepts are classes carrying their behaviour (e.g. a block computes its spec diff against its parent), not plain data structures handled by free functions. Applies from the class diagram (#2) on.
