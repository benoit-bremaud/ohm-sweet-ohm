# Project framing — Ohm Sweet Ohm

_Electronic schematics search API · Status: draft · 2026-10-08_

## Vision

Help electronics enthusiasts find a **reusable circuit block** that matches a
precise need ("5 V output from 7–15 V input, ≥ 1 A"), through a public API and a
demo web front-end.

## Goal

Learning / portfolio project. Design quality (UML-first, tests, CI, clean
architecture) takes precedence over catalogue volume.

## Decisions

| Topic | Decision | Deferred / later |
|---|---|---|
| Data source | Curated catalogue (open formats: KiCad, manufacturer app notes) | Aggregation of explicitly-licensed sources; community contributions via PR |
| Unit of content | Reusable functional block (regulator, preamp, H-bridge…) | Full projects composed of blocks |
| Search | v1: structured filters (category, numeric ranges, components, keywords) | v2: natural language → structured filters (LLM), semantic search (pgvector) |
| Response content | Metadata + rendered schematic (SVG) | Source file download, BOM, educational explanation |
| Reliability | Validation status (`tested` / `theoretical`) + cited source + high-voltage safety warning | Target: automated SPICE simulation from KiCad SPICE netlist, isolated service |
| Spec model | Typed parameters per category, stored as min/max ranges in SI units | — |
| Backend | TypeScript, Fastify, PostgreSQL (range types; pgvector in v2), OpenAPI from Zod schemas | — |
| Name | **Ohm Sweet Ohm** (repo/domain slug: `ohm-sweet-ohm`) | — |
| Front-end | Next.js (server rendering: one indexable page per base circuit and variant), typed client generated from OpenAPI | — |
| Hosting | Managed services: hosted PostgreSQL, API on a container platform, front on Vercel. Environments: local → staging (PR preview) → prod | — |
| Repository | Single repo, pnpm workspace (`apps/api`, `apps/web`, `apps/importer`, `packages/schemas`), catalogue in `catalogue/` with its own CC BY-SA license | Split catalogue repo if community contributions grow |
| Delivery | Vertical slices from M1; tracked with GitHub Project + milestones + issues. See WORKPLAN.md | — |
| Value calculator | v1: each base circuit stores its design formulas in the model | v2: per-circuit calculator returning component values rounded to standard series (E12…) |
| Consumers | Own web front + public API for third-party developers | — |
| API access | Anonymous read-only with rate limit; free API key for higher quotas; writes admin-only | — |
| Import pipeline | v1: CLI script in Docker (`kicad-cli` renders SVG) reading `<block>/schematic.kicad_sch` + `<block>/meta.yaml` | Catalogue git repo whose CI runs the same script on merge |
| Licensing | Code MIT; schematics CC BY-SA 4.0 | Per-schematic license field if third-party schematics are imported |
| Entry points | v1: browse by **base circuit** (voltage divider, regulator, transistor switch, op-amp…) and explore its variants; search by need via filters | Browse by **key component** (LM317, NE555…) — enabled by a block→key-component link |
| Variants | Tree: each variant has exactly one parent block. Rule: a variant keeps the parent's base topology; only values, additions or options change | Graph (multiple parents) if combinations become common |
| Variant diff | Short human text + spec differences vs parent computed by the API | Netlist-based component diff from KiCad |
| v1 catalogue | ~25 blocks (variants included) following a simple-to-complex progression of 5 base circuits: 1. LED + current-limiting resistor, 2. voltage divider, 3. RC filter, 4. transistor switch, 5. linear regulator | 6. NE555 timer, 7. op-amp |
| Difficulty | Each block has a level: beginner / intermediate / advanced (filterable) | — |
| Variant tree UX | Base circuit page with variant cards ("what changes") + breadcrumb | v2: side-by-side comparator (reuses the API spec diff) |
| Learning path | v1: an `order` field on base circuits | v2: "suggested next circuit" guided path |
| Timeline | A few hours per week; v1 in 2–3 months, 2-week milestones | — |

## Key insight

The hard part is the **data model**, not the API: a filter search is only as good
as the typed, unit-normalised specs behind each block. Model it first.

## Open questions

- Exact managed providers (database, API platform) — compare free tiers.
- Domain name availability for `ohm-sweet-ohm`.
- Typed parameters for each of the 5 v1 base circuits.

## Next steps

See milestone M0 in [WORKPLAN.md](WORKPLAN.md).
