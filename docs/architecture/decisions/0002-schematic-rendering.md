# ADR-0002 — Render catalogue schematics with KiCad in Docker, crop with Inkscape

- Status: accepted
- Date: 2026-10-10
- Deciders: Benoît Bremaud
- Related: issue #6 (spike), UC3 and UC6 in [01-use-case.md](../diagrams/catalogue/01-use-case.md),
  [catalogue-format.md](../specs/catalogue-format.md)

## Context and problem statement

Every block ships a KiCad 9 schematic. UC3 shows it rendered, and the API serves it to
third-party developers, so the rendering must be reproducible in CI and produce an image that
fits the drawing. `kicad-cli sch export svg` renders on a full page (A5 for the LED block, 210 ×
148 mm, with the circuit as a small island in the middle) and has no option to crop to the
drawing.

## Spike measurements (2026-10-10, KiCad 9.0.9)

| Measure | Result |
| --- | --- |
| `kicad/kicad:9.0.9` image (base, not `-full`) | 0.48 GB compressed, 1.67 GB unpacked, pulled in about 2 minutes on the local connection |
| Render of the LED block inside the image | 0.8 s; SVG identical to the local KiCad 9.0.9 render |
| Inkscape 1.2.2 added on top (Debian 12) | Image builds in 54 s, 1.81 GB (+140 MB) |
| Crop with `inkscape --export-area-drawing --export-margin=2` | 0.75 s; 210 × 148 mm page becomes 34 × 40 mm |
| ERC inside the base image | 6 `lib_symbol_issues` warnings: the base image has no symbol library tables. Not a schematic defect — schematics embed their symbols — but `--exit-code-violations` then fails |

## Considered options

1. **KiCad image plus Inkscape crop in CI** — one derived image, files cropped once at
   publication.
2. **Page-size SVG, cropped in the browser** with `getBBox()` at display time.
3. **Own cropper** computing the bounding box from the schematic or the SVG.

## Decision outcome

Chosen option: **1**, because cropped SVGs are then correct for every consumer — the web
front-end, third-party API clients, thumbnails — and are computed once, never per request.

- `docker/renderer/Dockerfile`: `kicad/kicad:9.0.9` pinned by digest, plus Inkscape.
- `scripts/render-catalogue.sh`: renders every `schematic.kicad_sch` to
  `build/catalogue/<base-circuit>/<block>/schematic.svg`, without the drawing sheet and the
  background, cropped with a 2 mm margin. Fails if no schematic is found.
- `.github/workflows/catalogue.yml`: runs only when the catalogue or the renderer changes, checks
  one SVG per schematic, uploads the SVGs as a 7-day artifact.
- Rendered SVGs are build output (`build/` is git-ignored). The importer (M1) will publish them.

### Consequences

- Good: one reproducible toolchain, pinned versions, tight images for every consumer.
- Good: rendering stays outside the domain; the domain only references the asset.
- Bad: a 1.8 GB image to build in CI; acceptable because the workflow runs only on catalogue or
  renderer changes. Publishing the image to a registry can cut the build time later if needed.
- Bad: Inkscape is GPL; it runs as a CI tool producing files and is never distributed with the
  MIT-licensed code.

### Follow-ups

- **ERC gating** (tooling backlog): the base image needs `--severity-error` (library-table
  warnings are environmental), or the `-full` image (1.1 GB compressed) with the libraries.
- **SVG safety**: today's SVGs come from curated schematics and contain no script. Once the
  catalogue accepts contributions, sanitize SVGs before serving them inline.
- **KiCanvas** (tooling backlog) may render `.kicad_sch` directly in the browser; the cropped
  SVG then remains the fallback, the API asset and the thumbnail source.
