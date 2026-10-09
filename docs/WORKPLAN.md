# Work plan — Ohm Sweet Ohm v1

_Status: validated draft · 2026-10-08 · cadence: a few hours/week, 2-week milestones, v1 in ~12 weeks_

See [FRAMING.md](FRAMING.md) for the decisions behind this plan.

## Principles

- **Vertical slices**: from M1 on, every milestone delivers something visible end
  to end (catalogue → database → API → Next.js page → PR preview), then widens.
- **UML-first**: each milestone models before it codes (diagrams in
  `docs/architecture/diagrams/<feature>/`).
- **Content grows with code**: one base circuit (with its variants) per milestone.
- **Every milestone ends shippable**: CI green, tests, `PROJECT_LOG.md` entry,
  merged via reviewed PRs (pre-push review gate).

## Repository layout

Single private repo `ohm-sweet-ohm`, pnpm workspace (no Turborepo/Nx in v1):

```
apps/api          Fastify + Zod, OpenAPI
apps/web          Next.js (server rendering)
apps/importer     CLI: validate meta.yaml, kicad-cli → SVG, upsert into PostgreSQL
packages/schemas  Shared Zod schemas (meta.yaml, API DTOs) — single source of truth
catalogue/        <base-circuit>/<block>/{schematic.kicad_sch, meta.yaml} + LICENSE (CC BY-SA 4.0)
docs/             architecture diagrams, API guide
```

Root `LICENSE` is MIT (code); `catalogue/LICENSE` is CC BY-SA 4.0 (schematics).

## Tracking

- GitHub Project for the repo; one GitHub milestone per M0–M5; one issue per task.
- `PROJECT_LOG.md` updated at every merge; this file updated when scope changes.

## Milestones

### M0 — Foundations & modelling (weeks 1–2)

- Repo, branch protection, Conventional Commits, pnpm workspace skeleton.
- CI: lint, typecheck, tests + security baseline (Gitleaks, CodeQL, dependency review).
- `README.md`, `PROJECT_LOG.md`, both licenses.
- UML: use-case diagram (Enthusiast, Third-party developer, Curator) and domain
  class diagram (Block, BaseCircuit, Variant link, ParameterDefinition, SpecRange,
  KeyComponent, Source, ValidationStatus, Difficulty, Formula).
- Typed parameters defined for **all 5** v1 base circuits (protects the model
  against rework in later slices).
- `meta.yaml` Zod schema in `packages/schemas`.
- Spike: `kicad-cli` SVG export inside Docker and in CI.

**Done when**: diagrams validated, CI green on the skeleton, spike conclusive.

### M1 — First vertical slice: LED + resistor (weeks 3–4)

- Content: **1. LED + resistor**, base block only.
- Importer: validate, render SVG, upsert. Idempotent.
- PostgreSQL schema + migrations (specs stored in SI units; search runs in memory, ADR-0001).
- API: `GET /blocks/{slug}` + SVG, OpenAPI + Swagger UI.
- Web: one block page (SVG, specs, source, validation status, safety warning).
- Deploy staging: managed PostgreSQL, API container, Vercel PR preview.

**Done when**: the LED page is reachable on a PR preview URL, fed end to end by the catalogue.

### M2 — Variant trees (weeks 5–6)

- Content: LED variants + **2. voltage divider** with variants.
- API: list base circuits (progression order), variant tree (children + breadcrumb),
  spec diff vs parent.
- Web: home page (progression), base circuit page with variant cards + breadcrumb.
- UML: sequence diagram "browse a base circuit's variants".

**Done when**: both circuits are navigable base → variant → back, diff highlighted.

### M3 — Search by need (weeks 7–8)

- Content: **3. RC filter**.
- API: filter search (base circuit, numeric criteria matched with the domain match modes
  `covers` / `within`, enum values, difficulty, key component, keywords), run in memory (ADR-0001).
- Web: search page with filters, SEO metadata per page.
- UML: sequence diagram "search by need".

**Done when**: "5 V out, beginner" style queries return the expected blocks, covered by tests.

### M4 — Public API (weeks 9–10)

- Content: **4. transistor switch**.
- Anonymous read with rate limit; free API keys for higher quotas; admin-only writes.
- API guide for third-party developers; OpenAPI-generated typed client used by web.
- UML: state diagram for the API key lifecycle if it carries real states.

**Done when**: a third party can obtain a key and query the API from the docs alone.

### M5 — Release v1.0.0 (weeks 11–12)

- Content: **5. linear regulator**.
- Production environment; catalogue import runs in CI on merge to `main`.
- Contribution guide for blocks; public release checklist, then repo goes public.
- Tag `v1.0.0`, `CHANGELOG.md`, LinkedIn post.

**Done when**: public URL live with the 5 base circuits, repo public, v1.0.0 tagged.

## After v1 (backlog, not scheduled)

- Natural language → structured filters (LLM), semantic search (pgvector).
- Side-by-side comparator, guided learning path, value calculator (E-series).
- Browse by key component, base circuits 6 (NE555) and 7 (op-amp).
- SPICE simulation service validating announced specs.
- Source file download, BOM, educational explanations.

## Risks

| Risk | Mitigation |
|---|---|
| Content entry slower than expected | Cut variants before cutting base circuits |
| Typed parameters wrong for later circuits | All 5 circuits modelled in M0 |
| `kicad-cli` friction in Docker/CI | Spike in M0; fallback: commit pre-rendered SVGs |
| Hosting setup eats M1 | Keep M1 slice minimal (one page, one endpoint) |
| Scope creep toward v2 features | Nothing enters a milestone without updating this plan |
