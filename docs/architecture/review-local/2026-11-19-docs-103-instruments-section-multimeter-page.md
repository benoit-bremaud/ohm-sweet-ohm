# Local review — ohm-sweet-ohm (branch docs/103-instruments-section-multimeter-page)

Milestone review closing part 0 of epic #79: the instruments section and its multimeter page (#103).

- Date: 2026-11-19
- Commit: 0eb2a73 (plus the Nice fixes of this report's commit)
- Scope: branch diff `origin/main...HEAD`
- Checks run: adversarial (fresh reviewer, 4 rounds) · design · docs · tests · security · correctness
- Verdict: ship as-is · Must 0 · Should 0 · Nice 0 open

## Adversarial review (#236)

- Round 1 on `95460d8`: Must 2 · Should 4 · Nice 6 · unverified 1 · Push gate: closed
- Round 2 on `ce7144a`: 2 Must fixed, 4 Should fixed, Nice fixed except the thermocouple reference (kept: the text names the thermal camera page next to the camera) · new Should 1 · Push gate: open
- Round 3 on `e35a1c7`: Should fixed · Nice 1 · Push gate: open
- Round 4 on `0eb2a73`: Nice fixed · Nice 3 (applied in this commit) · **Push gate: open**
- Optional second review (owner's own account): not run (never a gate step)

## Pre-merge gate (head SHA 0eb2a73)

| Step | Result |
| --- | --- |
| 1 Tests | ✅ vitest 284 · pytest 236 · test-local-ci 47 · test-attest 22 |
| 2 Coverage | web 95.41 % stmts / 93.41 % branches / 95 % funcs / 95.68 % lines (floor 80) · figures 99.94 % · docs 100 % (floor 90) |
| 3 SonarQube | ⏸ deferred to the pre-merge run (`--push`) |
| 4 Secrets | ✅ gitleaks clean (66 commits) · no tracked .env · diff read: nothing sensitive |
| 5 E2E/smoke | ⏸ deferred to the pre-merge run (`--push`); manual check on the dev server: `/depannage` and `/depannage/i1_multimetre` render, figures load, links alive, no overflow at 375 px |

- Gate: `--push`: **pre-push green** — `just check` passed, SonarQube and E2E deferred (never GREEN)

## 🔴 Must Have

- `troubleshooting/{10_resistance,13_fusible,22_condensateur_electrolytique}/README.md` `[adversarial]` · plural « fiches 03 et NN » references left over · fixed in `ce7144a`
- `troubleshooting/i1_multimetre/README.md` `[adversarial]` · the 10 A fuse check passed on a meter without a fuse · fixed in `ce7144a`: a low value proves a closed path, presence and type checked in the manual
- `apps/web/src/content.config.ts:18` `[tests]` · the widened glob had no negative case · fixed in `0eb2a73`: every folder holding a README must be loaded, so a misnamed folder fails the test

## 🟡 Should Have

- `troubleshooting/i1_multimetre/README.md` `[adversarial]` · mA/µA jack value, LED criterion, blown-fuse symptom · fixed in `ce7144a` and `e35a1c7`
- `scripts/figures/guide_i1.py` `[adversarial|tests]` · hard-coded 10 A jack position, no geometry test · fixed in `ce7144a` and `0eb2a73`
- `PROJECT_LOG.md` `[adversarial]` · missing entry · fixed in `ce7144a`
- `apps/web/src/pages/depannage/guides.test.ts` `[tests]` · weak menu assertion and stale `>= 12` count · fixed in `0eb2a73`
- `troubleshooting/gabarit.md:5`, `troubleshooting/README.md:11` `[docs]` · figure naming and outline of instrument pages · fixed in `0eb2a73` and this commit

## 🔵 Nice to Have

- `apps/web/src/content.config.ts` `[correctness|adversarial]` · `i[0-9]` also accepted `i0` · tightened to `i[1-9]` in this commit
- `apps/web/scripts/render-trees.ts:15`, `apps/web/src/lib/mermaid-trees.test.ts:26` `[design|adversarial]` · decision trees are read from numbered guides only · documented in both files and in `content.config.ts`
- `scripts/figures/guide_i1.py` `[design]` · unused variable · fixed in `0eb2a73`

## ⚪ Disagree / Intentional

- `troubleshooting/i1_multimetre/README.md` `[adversarial]` · sockets in CAT III follow IEC 61010-2-030
- `scripts/figures/test_figures.py` `[adversarial]` · the geometry test copies the meter placement of `fig_fuse`: a moved meter gives a false failure, never a false pass
- `scripts/figures/guide_i1.py:17` `[design]` · `_callout` keeps two floats instead of a `Point`: one module, seven calls, no gain worth the churn

## Per-dimension summary

- Adversarial: 2 Must on accuracy and safety, fixed and verified over 4 rounds · Design: ship as-is · Docs: template and glob documented · Tests: glob and figure geometry pinned · Security: static SVG, glob confined to `troubleshooting/` · Correctness: no bug
