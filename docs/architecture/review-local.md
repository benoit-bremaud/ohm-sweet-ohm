# Local review — ohm-sweet-ohm (feat/18-web)

- Date: 2026-10-15
- Commit: `670eb14` (branch head before push)
- Scope: branch diff main...HEAD (`apps/web`, root tooling, ADR-0003, diagrams 03 and 06, README, project log)
- Checks run: design · docs · tests · security · correctness (five independent read-only reviewers, reconciled) · `pnpm check` green under Node 22.23.3 (218 tests)
- Verdict: fix Must Have first · Must 1 · Should 8 · Nice 6
- Outcome (same day, before push): the Must, every Should and five Nice applied in the follow-up commit (229 tests); the deployment-level Nice (HSTS, `script-src 'none'`) filed as issue #24.

## 🔴 Must Have

- `packages/schemas/src/block-response.ts:46` `[design][security]` · `source.url` is only `z.string()`, so a drifted API could ship a `javascript:` link that the page renders in `href`; the input schema already restricts to http(s) · tighten the shared contract to `z.url({ protocol: /^https?$/ }).nullable()` and add an off-contract test.

## 🟡 Should Have

- `apps/web/src/lib/format.ts:27` `[correctness]` · rounding after choosing the prefix: `0.9996 A` gives `1,000 mA` · round to 3 significant digits first, `useGrouping: false`, tests at both boundaries.
- `apps/web/src/pages/blocks/[slug].astro:17-48` `[tests][correctness]` · the page's wiring (404 rewrite, 502 with `no-store`, hazard warning before the schematic) has no test · one page-level Container test with `fetch` stubbed.
- `apps/web/wrangler.jsonc:10`, `apps/web/src/lib/catalogue-api.ts:30` `[docs][correctness][security]` · default `API_URL` port 3100 (local workaround) contradicts the README; `new URL('/blocks/…', API_URL)` would drop a path · origin-only rule: default 3000, `new URL(API_URL).origin`, README says "origin".
- `apps/web/src/lib/catalogue-api.ts:4` `[design]` · slug regex copied a third time (api, schemas, web) · export `SLUG_PATTERN` from `packages/schemas`, use it in the API and the web app.
- `apps/web/src/components/{SpecTable,KeyComponents,Formulas}.astro` `[design]` · `.empty` ×3 (already drifting) and `.sr-only` ×2 · define both once in `global.css`.
- `apps/web/astro.config.ts:19`, `apps/web/src/middleware.ts:3` `[security]` · CSP is sent as a header, so `frame-ancestors 'none'` belongs in it; `Permissions-Policy` missing; middleware comment inaccurate · add both, fix the comment.
- `apps/web/src/lib/catalogue-api.ts:6,12`, `SafetyWarning.astro:4`, `Schematic.astro:20` `[docs]` · `BlockLookup` and `isSlug` undocumented; HTML comments are shipped to the browser · docstrings; `{/* */}` comments.
- `apps/web/src/components/components.test.ts:23-26` `[tests]` · invisible literal NBSP, assertions `>1<` / `>Red<` not anchored to their row · `NBSP` constant, row-anchored regexes.

## 🔵 Nice to Have

- `apps/web/src/pages/404.astro:3` `[correctness][security]` · no `cache-control` on the 404 · `max-age=60`, the API's freshness window.
- `apps/web/src/components/SpecTable.astro:23` `[design]` · enum capitalisation split between `formatSpec` and the component · capitalise in `formatSpec`.
- `apps/web/src/lib/format.ts:17`, `catalogue-api.ts:55` `[design]` · `number` and `describe` are misleading names · `threeDigits`, `messageOf`.
- `apps/web/src/middleware.ts`, `astro.config.ts` `[security]` · HSTS and `script-src 'none'` · deployment-level (zone HSTS, dev toolbar check); filed as a backlog issue for #19.
- `docs/architecture/diagrams/catalogue/06-sequence-view-block-page.md:35,47` `[docs]` · SVG request drawn outside the 200 branch; 404 label differs from the page · move the request into the branch, "no such page"; document the nano…giga bounds in `format.ts`.
- `apps/web/src/lib/format.test.ts`, `components.test.ts:61-105` `[tests]` · no `G` or negative row; breadcrumb first item unchecked; two components per test · add rows, assert the base circuit, split.

## ⚪ Disagree / Intentional

- `apps/web/src/lib/catalogue-api.ts:24` `[design]` · `fetchFn` default parameter is the minimal seam to replace the only boundary (network); no adapter layer · architecture skill (proportional seams).
- `apps/web/src/components/components.test.ts` `[tests]` · experimental Container API accepted with exact version pins · ADR-0003.
- `apps/web/src/astro-modules.d.ts:7` `[design]` · `export default` inside a module declaration mirrors the shape Astro imposes on components · ESLint override scoped to `*.d.ts`.

## Per-dimension summary

- Design: dependency rule holds (web → schemas only), proportionate components; one contract gap (URL scheme), two Rule-of-Three duplications · Docs: WHY comments throughout, two missing docstrings, one config/README mismatch · Tests: healthy pyramid (31 unit, 10 component), boundary-only mocking, page wiring untested · Security: SSRF closed by the slug allowlist, auto-escaping everywhere, CSP as a header with `default-src 'none'`; hardening only · Correctness: one rounding bug at prefix boundaries, 404 cache behaviour, otherwise sound including CI on a fresh clone.
