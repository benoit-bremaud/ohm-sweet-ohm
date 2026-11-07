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

- `docker/renderer/Dockerfile`: `kicad/kicad:9.0.9` pinned by digest, plus Inkscape pinned to
  `1.2.2-2+b1`, so a new version is always a deliberate change.
- `scripts/render-catalogue.sh`: renders every `schematic.kicad_sch` to
  `build/catalogue/<base-circuit>/<block>/schematic.svg`, without the drawing sheet and the
  background, cropped with a 2 mm margin. Paths are resolved from inside the catalogue, so any
  way of writing `CATALOGUE_DIR` works (checked on eight forms, including a trailing slash, an
  absolute path and a symbolic link). Fails if no schematic is found, and fails on a multi-sheet
  schematic: `kicad-cli` emits one SVG per sheet, and a block has a single rendered schematic.
- `just render` (originally `.github/workflows/catalogue.yml`, moved to the local gate in #68):
  builds the renderer image, renders every schematic and checks one SVG per schematic; runs in
  `just gate` and before every `just deploy staging`.
- Rendered SVGs are build output (`build/` is git-ignored). The importer (M1) will publish them.

### Consequences

- Good: one reproducible toolchain, pinned versions, tight images for every consumer.
- Good: rendering stays outside the domain; the domain only references the asset.
- Bad: a 1.8 GB image to build in the gate; acceptable because Docker caches its layers on the
  curator's machine. Publishing the image to a registry can cut the build time later if needed.
- Bad: Inkscape is GPL; it runs as a CI tool producing files and is never distributed with the
  MIT-licensed code.

### Follow-ups

- **ERC gating** (tooling backlog): the base image needs `--severity-error` (library-table
  warnings are environmental), or the `-full` image (1.1 GB compressed) with the libraries.
- **Importer (M1)**: if the importer calls `kicad-cli` directly instead of this script, it must
  keep the single-sheet check (one SVG emitted per block) and the crop check below.
- **Inkscape exit status is unreliable**: measured in the renderer image, it exits 0 on a missing
  input, an unwritable output and a malformed SVG (for which it even writes a 218-byte empty
  SVG). The script therefore checks the result — a non-empty SVG with a `viewBox`, and no message
  other than the harmless `GtkRecentManager` warning — and reports the block with Inkscape's
  message. `kicad-cli` is reliable: it exits 3 on a broken or missing schematic.
- **Registry**: publishing the renderer image and consuming it by digest becomes worthwhile when
  the M1 importer renders on every publication.
- **SVG safety**: today's SVGs come from curated schematics and contain no script. Once the
  catalogue accepts contributions, sanitize SVGs before serving them inline.
- **KiCanvas** (tooling backlog) may render `.kicad_sch` directly in the browser; the cropped
  SVG then remains the fallback, the API asset and the thumbnail source.
