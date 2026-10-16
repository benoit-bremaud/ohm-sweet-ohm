# UI review — `/blocks/[slug]` (before refresh) — 2026-10-16

**URL / build:** `http://localhost:4321/blocks/led-resistor-basic` (astro dev, API = Fly staging) @ `3501a91`
· **Tool:** Playwright MCP (Chromium) · **Widths:** 390 / 768 / 1440
**Mode:** Read (secondary: Operate — the spec table is scanned) · **Invention level:** Extend
(paper/ink/copper datasheet tokens from PR #25)

Screenshots: `2026-10-16-ui-review-block-before-1440.png`, `…-before-390.png`,
`…-before-768-dark.png`. The dark pill at the bottom of each capture is the Astro dev toolbar
(dev only, not shipped).

## Decisions in conflict with doctrine (not defects)

| Choice | Conflicts with | Decided on | Source | Reopen? |
| --- | --- | --- | --- | --- |
| Schematic colours are KiCad's (green wires, dark-red parts) | One accent, palette from the subject | PR #25 (ADR-0003: SVG rendered by the API, shown as `<img>`) | ADR-0003 | No — out of the web app's reach |

## Scores

| Dimension | Score /5 | Evidence |
| --- | --- | --- |
| Hierarchy | 3 | 1440: title and schematic lead, but every `h2` section has the same weight; the page reads as a plain document, not a datasheet |
| Typography | 2 | Computed `font-family` starts with `Inter`, not loaded → OS fallback (Ubuntu on this host); one weight contrast (400/600–700), no display face, `h1` 40 px only |
| Layout and rhythm | 2 | 1440: sections capped at 65ch inside a 72rem page → right ~45 % empty under the specs; header/footer full-bleed while content is centred, edges do not align |
| Colour and contrast | 2 | No contrast failure measured (0 pairs < 4.5:1), but copper appears nowhere on this page (no link): grey + ink only → the "tristounet" feeling |
| States | 3 | Focus ring visible (copper 2px); only one link state to judge; 502 state exists but is a bare heading + paragraph |
| Motion | 3 | None at all; nothing broken, nothing that tells the page is alive (no entrance, no hover feedback on rows) |
| Accessibility | 4 | Skip link 133×40 px (< 44 height, Should); landmarks, captions, `scope=row` OK; zoom unaffected |
| Content resilience | 4 | 390: no horizontal overflow (`docWidth` = `vw`), formula wraps, title block wraps in two columns |
| AI tells | 4 | No gradients, no cards rows, no eyebrows; mono used for data only |
| **Total** | **27/45** | |

## Findings

| # | Severity | Dimension | Evidence | Finding | Proposed fix |
| --- | --- | --- | --- | --- | --- |
| 1 | Should | Colour | 1440 capture | The accent is invisible: nothing on the page uses copper | Use copper on structural elements of a datasheet (rules, status, title-block tab, section markers) |
| 2 | Should | Typography | computed font = fallback | Declared `Inter` / `JetBrains Mono` never load; the type looks different per OS | Self-host one display/text family (Fontsource bundled by Astro, `font-src 'self'` in CSP) |
| 3 | Should | Layout | 1440 capture | Big empty right half below the specs; sections float left at 65ch | Two-column datasheet grid at ≥ 64rem: sheet + specs top, formulas/components/about in a second band |
| 4 | Should | Hierarchy | all captures | Validation status repeated (title block, about) and only as prose and never shown as a status | One status chip in the header, keep the title-block row |
| 5 | Should | Accessibility | skip link 133×40 | Target under 44 px | `min-block-size: 44px` |
| 6 | Nice | States | code read | 502 page is bare | Reuse the sheet frame for the error state |
| 7 | Nice | Motion | — | No feedback at all | Restrained CSS-only entrance + row hover, off under reduced motion |

## Checks

- Run: 3 widths full-page captures, measurement script at 1440 (overflow, targets, contrast),
  dark scheme at 768, visual pass at 390.
- Not run: reduced motion (page has no motion yet), Firefox/WebKit (not requested), hazardous
  block variant (no hazardous block in the staging catalogue).

## After the refresh (direction A, "drawing sheet", owner-validated 430/500)

Screenshots: `2026-10-16-ui-review-block-after-1440.png` (light),
`…-after-390-dark.png` (dark + reduced motion). Measured at 390 dark: `docWidth` = `vw` (no
overflow), 0 text pairs under 4.5:1, IBM Plex Sans 400/600 and Mono 400 loaded from `'self'`.

| Dimension | Before | After | Evidence |
| --- | --- | --- | --- |
| Hierarchy | 3 | 4 | Larger `h1`, status stamp under it, copper-ruled sections |
| Typography | 2 | 4 | IBM Plex self-hosted through Fontsource (bundled by Astro, `font-src 'self'`); values in Plex Mono |
| Layout and rhythm | 2 | 4 | Framed sheet aligns header, content and footer; notes band fills 1440 in three columns |
| Colour and contrast | 2 | 4 | Copper on the header rule, section rules, cartouche tab, stamp, formula tint; no contrast failure |
| States | 3 | 3 | Row hover tint added; error pages inherit the frame but stay plain text |
| Motion | 3 | 4 | One staggered entrance (280 ms, ease-out token), travel removed under reduced motion; row hover gated to fine pointers |
| Accessibility | 4 | 5 | Skip link `min-block-size: 44px` |
| Content resilience | 4 | 4 | 390: no overflow, cartouche tab spans both columns |
| AI tells | 4 | 4 | No new tell; the dot grid and zone ticks come from drawing paper |
| **Total** | **27/45** | **36/45** | |

Findings 1–5 (Should) fixed. Nice 6 partly (frame on every page), Nice 7 done: no backlog
issue left from this review.
