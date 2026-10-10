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

- **PR #8 merged** (`8a4bb39`) — docs(uml): add catalogue domain class diagram and typed parameters. Branch `docs/2-domain-class-diagram`, closes #2; review rounds: Codex ×2, Copilot ×3, all addressed. Content: `docs/architecture/diagrams/catalogue/04-class.md`, `docs/architecture/specs/base-circuits-parameters.md`, ADR-0001. Draft reviewed by an independent architecture review before push: 5 Must Have and 9 Should Have findings, all applied with owner validation; a verification pass found one unresolved point (unit check at publication) and four new Should Have items (explicit result objects, no SearchCriteria↔Catalogue cycle, typed matching without downcast, invariants checked after republication), all applied.
  - **Decisions**:
    - `Match mode fixed per parameter` — `covers` for what a circuit accepts or withstands, `within` for what it delivers; plain range overlap rejected (false positives), user-chosen mode rejected (complexity).
    - `BaseCircuit holds definitions, its root Block holds values` — single responsibility; the root block is the base circuit's own schematic.
    - `Hazard declared by the curator` — computing it would need AC/DC and context rules.
    - `Publication takes a draft with raw specs` — the domain itself reports unknown parameters, wrong types, missing parent and cycles; Zod only checks shapes at the boundary.
    - `Formulas shown in UC3` — gives the class a v1 use and prepares the v2 calculator.
    - `Search in memory (ADR-0001)` — one implementation of the match rules for ~25 blocks; PostgreSQL range types no longer required.
    - `Base circuits without a root block are not listed` — raised by review (Codex): parameters can be defined before the schematic; the base circuit appears once its root block is published. Forbidding rootless base circuits rejected (blocks progressive import).
    - `Separate outputCurrent (capacity, covers) and regulatedCurrent (setpoint, within)` — raised by review (Codex): one parameter could not match both "at least 500 mA" and "18–22 mA" requests. Mode-dependent matching rejected (special mechanism for one case).
    - `Shared keys have the same definition kind` — raised by review (Copilot): enum keys reused across base circuits must keep the same allowed values, so search validation never depends on which definition is found first. Enum criterion values are validated too, so a typo is reported instead of returning no match.
- **PR #9 merged** (`5957226`) — chore: set up pnpm workspace, tooling and CI baseline. Branch `chore/3-tooling-and-ci`, closes #3 and #4; CI green on `main` after merge. Content: pnpm workspace, strict TypeScript 6.0, ESLint (strict type-checked, named exports only), Prettier, Vitest, markdownlint, CI quality job and Gitleaks. Review rounds: Codex ×2 (config glob for nested packages, Node engines), Copilot ×1 (root typecheck), all addressed; CI fix: Gitleaks needs `pull-requests: read`.
  - **Decisions**:
    - `TypeScript 6.0, not 7` — typescript-eslint 8.71 supports TypeScript below 6.1; typed linting matters more than the native compiler for now.
    - `CodeQL and dependency review gated on a public repository` — the free plan offers them, and branch protection, only on public repositories; `pnpm audit --audit-level high` stands in, branch protection added to M5.
    - `GHSA-vfj7-8cjw-p6xm ignored` — no patched version; reached only through markdownlint-cli2 on the repository's own globs.
    - `engines.node = ^22.13.0 || ^24.0.0 || >=26.0.0` — exact intersection of ESLint and Vitest support.
    - `Typecheck the root before packages` — `pnpm -r` skips the root, so the step passed without running tsc.

## 2026-10-10

- **Electronics tooling backlog** (branch `docs/workplan-tooling-backlog`) — `docs/WORKPLAN.md` gains a prioritized table of tools that enrich the API and the front-end: KiCanvas, KiCad ERC and BOM export, KiDiff, ngspice, EEcircuit-engine, PCB Calculator formulas, KiBot, CircuitJS.
  - **Decisions**:
    - `Tools stay at the edges` — CI for file-producing tools, browser for interactive ones; the domain never depends on them.
    - `ngspice, not PSpice` — PSpice is commercial and has no headless use; ngspice ships with KiCad and runs in CI and, compiled to WebAssembly, in the browser.
    - `GPL/AGPL tools only as CI tools or links` — KiDiff, KiBot and CircuitJS never get bundled into the MIT-licensed code.
    - `Rejected: netlistsvg, SKiDL` — unmaintained since 2022, and not needed while the catalogue is curated by hand.
