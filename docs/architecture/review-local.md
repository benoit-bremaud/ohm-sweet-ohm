# Local review — ohm-sweet-ohm (feat/web-visual-refresh)

- Date: 2026-10-16
- Commit: working tree on `3501a91` (reviewed before the first commit of the branch)
- Scope: branch diff main...HEAD + uncommitted (apps/web visual refresh: tokens, framed sheet layout, IBM Plex via Fontsource, `font-src 'self'`, status stamp, notes band, entrance motion; UI review report and screenshots)
- Checks run: design · docs · tests · security + correctness (four independent read-only reviewers, reconciled) · `make check-local` green
- Verdict: ship after Should fixes · Must 0 · Should 6 · Nice 3
- Outcome (same day, before push): every Should applied, Nice items handled as below.

## Pre-merge gate (working tree on `3501a91`)

| Step | Result |
| --- | --- |
| 1 Tests | ✅ 231 tests in 14 files (`pnpm check`), API image smoke ✅, catalogue render ✅ |
| 2 Coverage | ⚠️ not measured: the repo has no coverage provider (`@vitest/coverage-v8` missing) and no doc counter — pre-existing gap |
| 3 SonarQube | ⚠️ not run: no `sonar-project.properties` in the repo — pre-existing gap |
| 4 Secrets | ✅ gitleaks clean · Semgrep clean · Trivy config + image clean · `pnpm audit --prod` clean · no tracked `.env` · diff read: nothing sensitive |
| 5 QA pass | ✅ full: 390/768/1440, light + dark, reduced motion; no overflow, 0 contrast failures; screenshots `docs/architecture/qa/2026-10-16-ui-review-block-*.png` |

- Gate: **steps 1, 4, 5 green; 2 and 3 not available in this repo** — owner call.

## 🔴 Must Have

_None._

## 🟡 Should Have

- `apps/web/src/layouts/Page.astro:65-70` `[design][correctness]` · `max-width: 80rem` coupled to an `82rem` media reset, `margin` overridden by `margin-inline`. · Applied: `width: min(var(--sheet-max), …)` + `margin: … auto`, media block removed.
- `apps/web/src/layouts/Page.astro:54` `[design]` · Raw `44px`. · Applied: `--target-min` token.
- `apps/web/src/layouts/Page.astro:75-85` `[correctness]` · `no-repeat` inert on a repeating gradient; decorative overlay without `pointer-events: none`. · Applied.
- `apps/web/src/styles/global.css` `@keyframes enter` `[docs]` · Comment described a fill mode set elsewhere. · Applied: reworded.
- `docs/architecture/qa/2026-10-16-ui-review-block.md:38,40` `[docs]` · Font fix said `public/fonts` (implementation uses Fontsource); "3×" listed two places. · Applied.
- `apps/web/src/pages/blocks/slug.test.ts:66` `[tests]` · Stamp regex coupled to the `<p>` tag. · Applied: asserts class + label only.

## 🔵 Nice to Have

- `global.css` `--duration-press` used for hover `[design][docs]` · Applied: renamed `--duration-feedback`.
- `SafetyWarning.astro:6` `<strong>` asks for 700, only 400/600 loaded `[design]` · Applied: `strong, b { font-weight: 600 }`.
- `[slug].astro` two ternaries map the validation status to text `[design]` · Deferred: two uses, below the rule of three; a `Record<ValidationStatus, …>` when a third status arrives.

## ⚪ Disagree / Intentional

- `class:list={['stamp', block.validationStatus]}` uses the enum as a class: simple, covered by the stamp test.
- No unit test for CSS (grid, motion, CSP string): proportionality, verified on the render instead.

## Per-dimension summary

- Design: no over-engineering, tokens only, no inline style, no script. · Docs: comments WHY-oriented, report matches code. · Tests: proportionate, container level, one stubbed boundary. · Security: `font-src 'self'` correct (fonts emitted under `/_astro/`), OFL licences. · Correctness: CSS valid, reduced motion keeps the fade only.
