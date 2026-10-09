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
- **PR #7 merged** (`fed13fa`) — docs(uml): add catalogue use-case diagram. Branch `docs/1-use-case-diagram`, closes #1; two review rounds (Codex ×3, Copilot ×2), all addressed. Content: `docs/architecture/diagrams/catalogue/01-use-case.md`: six v1 use cases with Cockburn specifications, four v2 use cases shown dashed.
  - **Decisions**:
    - `Third-party developer generalizes Electronics enthusiast` — same goals through another channel; web and API are channels, not actors.
    - `Declaring a variant is publishing a block with a parent` — a separate use case would duplicate the publication flow.
    - `Fully object-oriented domain` — domain concepts are classes carrying their behaviour (e.g. a block computes its spec diff against its parent), not plain data structures handled by free functions. Applies from the class diagram (#2) on.
    - `API keys: GitHub sign-in, one active key per account` — raised by review (Copilot): unrestricted issuance let a developer bypass the quota by requesting new keys. The quota is tied to the account; a new key revokes the old one. Email verification rejected (disposable addresses), manual issuance rejected (does not scale).
    - `No per-block license in v1` — raised by review (Copilot): the catalogue keeps a single CC BY-SA 4.0 license, as framed.

## 2026-10-09

- **Domain class diagram and typed parameters** (branch `docs/2-domain-class-diagram`, issue #2) — `docs/architecture/diagrams/catalogue/04-class.md`, `docs/architecture/specs/base-circuits-parameters.md`, ADR-0001. Draft reviewed by an independent architecture review before push: 5 Must Have and 9 Should Have findings, all applied with owner validation; a verification pass found one unresolved point (unit check at publication) and four new Should Have items (explicit result objects, no SearchCriteria↔Catalogue cycle, typed matching without downcast, invariants checked after republication), all applied.
  - **Decisions**:
    - `Match mode fixed per parameter` — `covers` for what a circuit accepts or withstands, `within` for what it delivers; plain range overlap rejected (false positives), user-chosen mode rejected (complexity).
    - `BaseCircuit holds definitions, its root Block holds values` — single responsibility; the root block is the base circuit's own schematic.
    - `Hazard declared by the curator` — computing it would need AC/DC and context rules.
    - `Publication takes a draft with raw specs` — the domain itself reports unknown parameters, wrong types, missing parent and cycles; Zod only checks shapes at the boundary.
    - `Formulas shown in UC3` — gives the class a v1 use and prepares the v2 calculator.
    - `Search in memory (ADR-0001)` — one implementation of the match rules for ~25 blocks; PostgreSQL range types no longer required.
