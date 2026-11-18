# Local review — ohm-sweet-ohm (feat/123-troubleshooting-guide-pages)

Pre-push review of the troubleshooting guide pages of issue #123.

- Date: 2026-11-18
- Commit: 15058e4 (checks), followed by this report and wording-only doc fixes
- Scope: branch diff `main...HEAD`
- Checks run: adversarial (fresh reviewer, 3 rounds) · design · docs · tests · security · correctness
- Verdict: ship · Must 0 · Should 0 · Nice 5 (filed as follow-ups)

## Adversarial review (#236)

- Round 1 on `243b8c3`: Must 3 · Push gate: closed (no Chromium on Workers Builds; prerendered pages without hardening headers; stale "on demand only" statements).
- Round 2 on `c7f94ab` (committed SVG, `public/_headers`, ADR-0003 amended): 3 Must fixed · new Must 1 (WORKPLAN/FRAMING) · Should 3 · Push gate: closed.
- Round 3 on `15058e4`: all fixed · new Must 0 · Should 0 · Nice 2 (applied in the report commit) · **Push gate: open**.
- Optional second review (owner's own account): not run (never a gate step).

## Pre-merge gate (head SHA 15058e4)

| Step | Result |
| --- | --- |
| 0 CI mirror | n/a — no PR workflow (local CI only) |
| 1 Tests | ✅ 284 vitest (104 web) · local-ci 41 · attest 22 · figures 227 |
| 2 Coverage | tests 95.41 % stmts / 93.41 % branches / 95 % funcs / 95.67 % lines (floor 80) · docs 100 % (floor 90) |
| 3 SonarQube | ⏸ deferred to the pre-merge run (`--push`) |
| 4 Secrets | ✅ gitleaks clean (77 commits) · no tracked .env · diff read: nothing sensitive |
| 5 E2E/smoke | ⏸ deferred to the pre-merge run (`--push`) |

- Gate: **pre-push green** — `just check` exit 0; pnpm audit passes with the existing recorded waivers; zizmor ran offline.

## 🔴 Must Have

_None._

## 🟡 Should Have

_None._

## 🔵 Nice to Have

- `apps/web/src/lib/mermaid-trees.ts:7` `[adversarial]` · block counting by regex vs mdast code nodes can diverge on nested fences · follow-up issue.
- `apps/web/src/lib/flowchart-text.ts:48` `[adversarial]` · unknown standalone node shapes are dropped silently · throw on any line not understood.
- `apps/web/scripts/render-trees.ts:15` `[adversarial]` · SVGs deleted before render; a failed render leaves a guide without them · render first, then replace.
- `apps/web/src/pages/depannage/index.astro` `[adversarial]` · links without trailing slash cost a 307 on Cloudflare assets · align `trailingSlash` or links.
- `apps/web/src/components/GuideProse.astro:42` `[design]` · `display: block` on tables loses table semantics for some screen readers · wrap tables in a scroll container instead.

## ⚪ Disagree / Intentional

- `docs/architecture/decisions/0003-web-astro-cloudflare.md:72` `[adversarial]` · original sentence kept, amendment appended · ADR amendment practice.

## Per-dimension summary

- Adversarial: 3 rounds, gate open · Design: committed SVG removes the build-time browser · Docs: ADR-0003, diagrams, WORKPLAN, FRAMING, deploy, gabarit aligned · Tests: every guide is a fixture (links, alts, diagrams, staleness) · Security: strict CSP, no `data:` images, `_headers` for prerendered pages, SVGs scanned clean · Correctness: build without Chromium verified.
