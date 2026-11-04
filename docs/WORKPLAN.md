# Work plan — Ohm Sweet Ohm v1

Status: validated draft · 2026-10-08 · cadence: a few hours/week, 2-week milestones, v1 in ~12 weeks

See [FRAMING.md](FRAMING.md) for the decisions behind this plan.

## Principles

- **Vertical slices**: from M1 on, every milestone delivers something visible end
  to end (catalogue → database → API → Astro page → branch preview), then widens.
- **UML-first**: each milestone models before it codes (diagrams in
  `docs/architecture/diagrams/<feature>/`).
- **Content grows with code**: one base circuit (with its variants) per milestone.
- **Every milestone ends shippable**: CI green, tests, `PROJECT_LOG.md` entry,
  merged via reviewed PRs (pre-push review gate).

## Repository layout

Single public repo `ohm-sweet-ohm` (public since 2026-11-07), pnpm workspace (no Turborepo/Nx in v1):

```text
apps/api          Fastify + Zod, OpenAPI
apps/web          Astro on Cloudflare Workers (server rendering on demand, ADR-0003)
apps/importer     CLI: validate meta.yaml, read the SVG rendered by docker/renderer (just render), upsert into PostgreSQL
packages/schemas  Shared Zod schemas (meta.yaml, API DTOs) — single source of truth
catalogue/        <base-circuit>/<block>/{schematic.kicad_sch, meta.yaml} + LICENSE (CC BY-SA 4.0)
studies/          <study>/ README + KiCad files, outside the v1 catalogue + LICENSE (CC BY-SA 4.0), see #47/#56
docs/             architecture diagrams, API guide
```

Root `LICENSE` is MIT (code); `catalogue/LICENSE` is CC BY-SA 4.0 (schematics); `studies/LICENSE` (created in #56) will be CC BY-SA 4.0 too. Course sheets are CC BY-SA 4.0 as well, in a folder and with a licence file chosen in #58.

## Tracking

- GitHub Project for the repo; one GitHub milestone per M0–M5; one issue per task.
- `PROJECT_LOG.md` updated at every merge; this file updated when scope changes.

## Milestones

### M0 — Foundations & modelling (weeks 1–2)

- Repo, branch protection, Conventional Commits, pnpm workspace skeleton.
- Checks: lint, typecheck, tests + security baseline (gitleaks, Semgrep, Trivy, `pnpm audit`), local
  since #68 (`just check` / `just gate`, `docs/deploy.md` § Local CI); GitHub Actions deploys a signed tag only.
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
- Deploy staging: managed PostgreSQL, API container, Cloudflare Workers branch preview.

**Done when**: the LED page is reachable on a branch preview URL, fed end to end by the catalogue.

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

### M4 — Value calculator (weeks 9–10)

- Content: **4. transistor switch**.
- UML first: calculator classes in the class diagram (calculation modes per base circuit,
  standard series, checks), sequence diagram "compute component values" (UC10).
- Domain: explicit calculation modes per base circuit, both ways (target to components,
  components to result) — no general equation solver; E12/E24 rounding with the real result and
  its deviation; power dissipated per resistor; base-circuit checks (LED and pin current limits,
  transistor saturation, LM317 dropout); step-by-step formula with values substituted.
- Presets: LED forward voltage by colour, common supplies, microcontroller pin current limits.
- API: calculation endpoint per base circuit (UC10 for third-party developers).
- Web: calculator on each block page, prefilled with the block's values; calculators index page;
  input as a numeric field plus a unit-prefix list with a default per field (kΩ for a resistor,
  mA for an LED current), as on DigiKey and the other surveyed calculators, which also brings the
  numeric keypad on phones; shareable link reproducing a calculation.
- Calculators for base circuits 1–4; the linear regulator's comes with its content in M5.

**Done when**: for base circuits 1–4, both directions work in the web front-end and through the
API — a target value gives buildable E12/E24 values with their real result, and component values
give the result — each with resistor power and the base circuit's warnings.

### M5 — Release v1.0.0 (weeks 11–12)

- Content: **5. linear regulator**, with its calculator (LM317 dropout check).
- Public API: anonymous read with rate limit, admin-only writes; API guide for third-party
  developers; OpenAPI-generated typed client used by web.
- Production environment (second Fly app and Neon branch, ending the shared-app derogation);
  catalogue import runs in `just deploy staging`.
- Contribution guide for blocks; rulesets on `main` and on `v*` tags (the repository is public
  since #68, so they are available).
- Tag `v1.0.0`, `CHANGELOG.md`, LinkedIn post.

**Done when**: public URL live with the 5 base circuits, repo public, v1.0.0 tagged.

## Outside the milestones (in parallel, time-boxed)

Two workstreams run alongside v1 for learning purposes. They **never displace a milestone
deliverable**: they take at most about a quarter of the weekly hours, and v1 issues (M2 first)
come before them. Decisions and matrices are in `PROJECT_LOG.md` (2026-11-04).

- **Circuit studies** (epic #47): `studies/<study>/` with KiCad schematic, routed PCB and
  README, status `theoretical`, outside `catalogue/`. First study: the Li-ion charger family
  (epic #48, sub-issues #51–#55), prerequisites #56 (template, licence, KiCad checks) and #57
  (Li-ion safety flag decision).
- **Component course sheets** (epic #50): Markdown sheets, components before circuits; template
  #58, v1 components #59, charger components #60. Ordering with studies: in parallel, each
  study pulls the sheets of its own components.

## After v1 (backlog, not scheduled)

- **Realistic component view (first item after v1)**: real-looking components drawn on the
  geometry of each block's KiCad schematic (positions, rotations, values and wires extracted at
  publication into a small layout file), so every block and variant gets it with no curation and
  it always matches the schematic. Resistor colour bands follow the value and the LED brightness
  follows the computed current, live with the calculator. A per-base-circuit breadboard template
  was rejected (each variant adding a component needs a new template); automatic breadboard
  placement stays a later evolution built on the same layout data.
- Natural language → structured filters (LLM), semantic search (pgvector).
- API keys (UC5): GitHub sign-in, one active key per account, higher quotas — moved out of v1
  when the value calculator took M4.
- Calculator extras: combination of two standard resistors, resistor colour code, tolerance
  worst case and load effect, curves.
- Side-by-side comparator, guided learning path (a component-first path: #61).
- Browse by key component (with the component sheets: #61), base circuits 6 (NE555) and 7 (op-amp).
- Publication of studies and their routed PCBs through importer, API and web (#49).
- Source file download, BOM, educational explanations (the course sheets above).

## Electronics tooling backlog

Tools that enrich the API and the web front-end. They stay at the edges: in CI for anything that
produces files, in the browser for anything interactive. The domain never depends on them. Each
entry becomes a decision (and, where the model changes, a UML update) when it is scheduled. The
**Target** column defines when an entry may enter the plan; a "v1" target never displaces a
milestone deliverable.

| Priority | Tool | Use in Ohm Sweet Ohm | Where it runs | License | Target |
| --- | --- | --- | --- | --- | --- |
| 1 | KiCanvas | Interactive schematic viewer on the block page (zoom, pan, hover a component) instead of a static SVG | Browser | MIT | v1, on the block page (built from M1), only in a milestone with slack; else first v1.x item |
| 2 | KiCad ERC (`kicad-cli sch erc --exit-code-violations`) | Reject a block whose schematic fails the electrical rules check at publication (new UC6 extension); without the flag the command exits 0 even when it finds violations | CI / importer | GPL-3.0 (KiCad, used as a tool) | v1.x |
| 3 | KiCad BOM export | Extract components from the schematic and cross-check the declared key components | CI / importer | GPL-3.0 (tool) | v1.x |
| 4 | KiDiff | Visual diff between a variant and its parent, shown in the variant tree (UC2) | CI | GPL-2.0 (tool only, output files) | v1.x |
| 5 | ngspice (KiCad SPICE netlist export) | Simulate blocks at publication, check announced specs, add a `SIMULATED` validation status, publish result curves | CI | BSD-3-Clause / GPL parts (tool) | v2 |
| 6 | EEcircuit-engine | ngspice in the browser: interactive simulation where the enthusiast changes a value and sees the curve update | Browser | MIT | v2 |
| 7 | KiCad PCB Calculator formulas | Re-implemented, not called (no CLI): E-series rounding, LM317 resistor pair, resistor colour code — feeds the value calculator (UC10) | Domain | — (formulas) | v2 |
| 8 | KiBot | Replace `docker/renderer`'s `kicad-cli` orchestration only if the pipeline grows beyond a few commands | CI | AGPL-3.0 (tool only) | When needed |
| 9 | CircuitJS (Falstad) | "See it run" link from each block to an animated simulation | Link to falstad.com | GPL-2.0 (linked, not embedded) | When the catalogue grows |
| 10 | Wokwi elements | Realistic resistor (colour bands from the value), LED (colour, brightness), potentiometer, photoresistor and thermistor for the realistic component view; transistor, capacitor, LM317 and supply drawn in-house | Browser | MIT | First item after v1 |

Constraints:

- **SPICE models**: base circuits 1–4 simulate with ngspice primitives; vendor models (e.g. LM317)
  are usually not redistributable — publish results and a model reference only.
- **Simulated is not tested**: `SIMULATED` stays distinct from `TESTED` (measured on a breadboard).
- **Simulation runs at publication**, never per request; the API serves precomputed results.
- **GPL/AGPL tools** run in CI and are never bundled into the MIT-licensed code; CircuitJS is
  linked, not embedded.
- **Rejected**: netlistsvg (unmaintained since 2022, KiCad already renders); SKiDL (circuits as
  code, not needed while the catalogue is curated by hand); PSpice (commercial, no headless use —
  ngspice covers the need).

## Risks

| Risk | Mitigation |
| --- | --- |
| Content entry slower than expected | Cut variants before cutting base circuits |
| Typed parameters wrong for later circuits | All 5 circuits modelled in M0 |
| `kicad-cli` friction in Docker/CI | Spike in M0; fallback: commit pre-rendered SVGs |
| Hosting setup eats M1 | Keep M1 slice minimal (one page, one endpoint) |
| Scope creep toward v2 features | Nothing enters a milestone without updating this plan |
