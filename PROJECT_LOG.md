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

- **PR #10 merged** (`87b20ef`) — docs(plan): add electronics tooling backlog. Branch `docs/workplan-tooling-backlog`; review rounds: Codex ×1, Copilot ×1, all addressed. Content: `docs/WORKPLAN.md` gains a prioritized table of tools that enrich the API and the front-end: KiCanvas, KiCad ERC and BOM export, KiDiff, ngspice, EEcircuit-engine, PCB Calculator formulas, KiBot, CircuitJS.
  - **Decisions**:
    - `Tools stay at the edges` — CI for file-producing tools, browser for interactive ones; the domain never depends on them.
    - `ngspice, not PSpice` — PSpice is commercial and has no headless use; ngspice ships with KiCad and runs in CI and, compiled to WebAssembly, in the browser.
    - `GPL/AGPL tools only as CI tools or links` — KiDiff, KiBot and CircuitJS never get bundled into the MIT-licensed code.
    - `Rejected: netlistsvg, SKiDL` — unmaintained since 2022, and not needed while the catalogue is curated by hand.
  - **Review round 2** (Copilot ×1): the tooling backlog was nested under "After v1 (backlog, not scheduled)" while KiCanvas targeted v1, and its target wrongly named M4 (the public API milestone) as the front-end one. The tooling backlog is now a top-level section whose Target column defines scheduling, and KiCanvas targets the block page built from M1, only in a milestone with slack.
- **PR #11 merged** (`fc52db8`) — feat(schemas): add meta.yaml reader and first LED catalogue block. Branch `feat/5-catalogue-format`, closes #5. Content: `docs/architecture/specs/catalogue-format.md`, first package `packages/schemas` (Zod 4.6, yaml 2.9, 68 Vitest tests), first block `catalogue/led-resistor/led-resistor-basic/` and the CC BY-SA 4.0 legal text in `catalogue/LICENSE` (downloaded from creativecommons.org with owner approval). The KiCad 9 schematic was generated from the official KiCad libraries by a one-off script and validated locally: ERC 0 violations, netlist +5V → R1 → D1 anode → D1 cathode → GND, SVG export. Independent code review before push: 2 Must, 4 Should, 3 Nice, then a verification pass with 1 new Should and 3 Nice — all applied.
  - **Decisions**:
    - `Readable value notation` — `5 V`, `7 V .. 15 V`, integer counts and lowercase words; a structured `{min, max, unit}` notation rejected as too verbose for curators.
    - `Layout catalogue/<base-circuit>/<block>/` — the variant tree lives in `parent`, never in folders, so moving a variant never moves a folder.
    - `Spec values read as written` — a second, failsafe YAML parse keeps spec scalars as text, so `1e3`, `1.0` or `0x10` never become numbers before the notation is checked.
    - `Every error reported` — spec checks run inside the schema, one issue per key, so no invalid entry hides another.
    - `Boundary only` — the package checks shape and notation; known keys, required parameters, parent and change summary stay domain rules (04-class.md).
  - **Noted for later**: the KiCad `Device:LED` symbol has no SPICE model mapping (SPICE netlist export shows `D1` without nodes); to handle with the ngspice backlog item.
  - **Review round 1** (Codex ×1, Copilot ×3), each studied further before deciding, on the owner's request:
    - `Decimal shift instead of multiply-then-round` — measuring float behaviour showed the 12-digit rounding was the common cause of two comments (a reversed range like `1.000000000001 V .. 1 V` accepted; a tiny value silently becoming 0) and also silently altered valid 13–14 digit values. Values now convert in one step (`13.6e-3`), with at most 15 significant digits and out-of-range rejection.
    - `Word-specific error message` — tightening the enum word rule alone would have reported `red-` as an invalid number; any text starting like a word now gets "must be a lowercase kebab-case word". Checked that all 23 enum values of the parameter spec still pass.
    - `Alias bomb returns an error` — YAML alias expansion beyond the parser limit is caught and reported as invalid YAML, since the catalogue will later accept contributions.
- **PR #12 merged** (`e310e1a`) — feat(catalogue): render schematics to cropped SVG in Docker and CI. Branch `spike/6-kicad-render`, closes #6; M0 complete once PR #10 is merged. Content: `docker/renderer/Dockerfile` (`kicad/kicad:9.0.9` pinned by digest + Inkscape), `scripts/render-catalogue.sh`, `.github/workflows/catalogue.yml`, ADR-0002. Measured: base image 1.67 GB, render 0.8 s and identical to the local render, Inkscape crop 0.75 s (210 × 148 mm page to 34 × 40 mm), derived image 1.81 GB built in 54 s.
  - **Decisions**:
    - `Crop with Inkscape in CI` — cropped SVGs serve the front-end, API clients and thumbnails alike, computed once; cropping in the browser or writing an own cropper rejected.
    - `Rendered SVGs are build output` — `build/` git-ignored; the importer (M1) publishes them.
  - **Finding**: the base KiCad image has no symbol library tables, so ERC reports 6 `lib_symbol_issues` warnings and `--exit-code-violations` fails. ERC gating (tooling backlog) needs `--severity-error` or the `-full` image.
  - **Review round 1** (Codex ×2), studied in depth on the owner's request:
    - `Resolve block paths from inside the catalogue` — reproduced: a trailing slash or an absolute path wrote SVGs to the wrong place. Of two fixes tested on eight path forms, stripping the trailing slash failed on `catalogue//` and broke symbolic links (find no longer follows them); resolving paths from inside the catalogue passed all eight.
    - `Reject multi-sheet schematics` — reproduced with a two-sheet schematic: `kicad-cli` emits one SVG per sheet and the script dropped the second silently. Rendering every sheet rejected (would change the domain model, API and UI for a need v1 does not have); an explicit failure checks an assumption the model already makes. Rule added to the catalogue format; the M1 importer must keep it.
  - **Review round 2** (Copilot ×2), studied in depth:
    - `Pin Inkscape to 1.2.2-2+b1` — the base image was digest-pinned but Inkscape floated with the Debian index. Package pin chosen (one line, any change becomes deliberate); a dated Debian snapshot rejected (fragile mirror for byte-level reproducibility a rendering does not need); publishing the image by digest deferred to M1.
    - `Check the crop result, not Inkscape's exit status` — Copilot flagged hidden diagnostics; measuring showed the deeper defect: Inkscape exits 0 on a missing input, an unwritable output and a malformed SVG (writing a 218-byte empty SVG). The script now checks for a non-empty SVG with a `viewBox` and no unexpected message, reports the block with Inkscape's message and fails. Verified in the image with a read-only output and a simulated malformed crop.
- **Milestone M0 closed** — issues #1–#6 done through PRs #7–#12; CI green on `main`.

## 2026-10-12

- **Debrief: online calculators survey** (branch `docs/calculator-in-v1`) — surveyed per-circuit calculators (DigiKey, Circuit Digest, electronics2000, Every Calculators, KSP, Ohmdox, RobotDyn, Kunkune) and reference design libraries (DigiKey, TI PowerLab, Würth REDEXPERT). Finding: calculators are what makers use, but none combines search by need, variants, standard values and an API; reference libraries search by specs but are vendor-tied, power-only and not pedagogical.
  - **Decisions**:
    - `Value calculator in v1 (M4)` — UC10 moves from v2 to v1: both ways via explicit calculation modes per base circuit (no general solver), E12/E24 values with real result and deviation, resistor power, base-circuit checks, step-by-step formula, presets, notation input, shareable link; on block pages, an index page and the API. Milestone M4 renamed "M4 — Value calculator".
    - `API keys (UC5) after v1` — keeps the 12-week calendar; v1 API stays anonymous read-only with rate limit, moved to M5 with the API guide. Adding a 14th week was rejected.
    - `Deferred calculator extras` — two-resistor combinations, colour code, tolerance and load, curves.
    - `Calculator input: numeric field plus unit-prefix list` — raised by review (Codex): the plan promised `4.7k`, which the catalogue parser rejects. Deeper study: every surveyed calculator uses a numeric field with a unit selector, and a numeric field brings the phone keypad; with a default prefix per field it is nearly as fast as free text. Free text with IEC 60062 codes (`4k7`) and text with a mandatory unit rejected; the catalogue notation stays for catalogue files and the API.
    - `M4 done when both directions work` — raised by review (Codex): the acceptance criterion only covered target-to-components.
    - `Stale schedule references fixed` — raised by review (Codex): the class diagram and the parameter spec still placed the calculator in v2 and UC5 in M4.
    - `Realistic component view, first item after v1` — real-looking components drawn on each block's KiCad geometry (layout extracted at publication; Wokwi elements, MIT, plus in-house drawings), animated by the calculator. Weighted score 4.55/5 against a per-base-circuit breadboard template (3.60, needs a template per variant adding a component), automatic breadboard placement (4.30 but low feasibility, kept as a later evolution), a KiCad 3D render (2.85) and a hand-drawn Fritzing view (2.05, drifts from the schematic).
- **PR #13 merged** (`80da2d6`) — docs(plan): bring the value calculator into v1. Codex ×3 addressed; merged without Copilot (no credits left, owner decision 2026-10-14).

## 2026-10-14

- **M1 planned** — six issues #14–#19: domain, database, importer, API, web page, deployment; access library, SVG storage and hosting providers decided at the start of their PR after a comparative study.
- **Domain package** (branch `feat/14-domain`, issue #14) — `packages/domain`, no dependency: typed specs and parameter definitions, `BaseCircuit.specsFrom`, immutable `Block`, `Catalogue.publish` with every 04-class.md invariant (unique slug and in-place republication, at most one root per base circuit, parent in the same base circuit, no cycle, change summary rule, descendants relinked on republication, shared-key consistency), and the LED + resistor base circuit. 43 domain tests. Search, variant diff and calculator left to M2–M4 (YAGNI).
  - **Independent review before push**: 1 Must (a NaN or infinite value made `publish` throw instead of reporting an error; mutation-checked test added), Should items applied (blank change summary counts as missing, clear message for a missing range end, duplicate enum values refused, invariant test gaps). One finding rejected after checking: count rejection tests already existed.
