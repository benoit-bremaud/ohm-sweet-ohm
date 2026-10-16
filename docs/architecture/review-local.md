# Local review — ohm-sweet-ohm (chore/local-coverage-sonar)

- Date: 2026-10-16
- Commit: `7d0fd09` reviewed; fixes applied in the next commit
- Scope: branch diff main...HEAD (coverage-v8 thresholds, doc-coverage counter and 31 doc blocks, `sonar-project.properties`, `make sonar-scan`, importer refactor for Sonar, docs)
- Checks run: design · docs · tests · security + correctness (four read-only reviewers, reconciled)
- Verdict: fix Must Have first · Must 1 · Should 5 · Nice 3
- Outcome (same day, before push): the Must and every Should applied except one Disagree, Nice handled as below.

## Pre-merge gate (head SHA, after fixes)

- **1 Tests**: ✅ 232 unit/integration · ✅ `make smoke-api` (container healthy) · ✅ catalogue render
- **2 Coverage**: tests 95.5 % stmts / 93.9 % branches / 95 % funcs / 95.9 % lines (floor 80, each package) · docs 100 % (77/77, floor 90)
- **3 SonarQube**: ✅ PASSED (new coverage 95.7 %, duplication 0 %, 0 new issues)
- **4 Secrets**: ✅ gitleaks clean (main..HEAD, 3 commits) · no tracked `.env*` · diff read: no token value, only the token variable name and path
- **5 QA pass**: no-UI tooling diff: `make check-local` run end to end on the real artefacts (API image built, started, healthy; scan uploaded)

- Gate: **GREEN — merge authorised** after owner approval.

## 🔴 Must Have

- `packages/domain/src/base-circuit.ts:13` `[docs]` · the new doc said "the first validation error" but `SpecsResult` carries every error · fixed: "every validation error found".

## 🟡 Should Have

- `Makefile` `sonar-scan` `[security|correctness]` · an old `coverage/lcov.info` could be uploaded on a direct run · fixed: refuses a report older than any `src` file.
- `Makefile` `sonar-scan` `[design]` · no empty `GIT_COMMON_DIR` guard unlike `sast`, overlong lines · fixed: same guard, lines wrapped.
- `apps/importer/src/read-catalogue.test.ts:7` `[tests]` · first assertion restated the implementation, ASCII only · fixed: literal order with a non-ASCII name, equality case.
- `vitest.config.ts:7` `[tests]` · `PACKAGES` kept by hand · fixed: comment that a new package must be added.
- `packages/db/src/migrations/0002-schematics-and-content-hash.ts:24` `[docs]` · doc restated the file name · fixed.

## 🔵 Nice to Have

- `scripts/doc-coverage.mjs` `[correctness]` · a non-doc `/* */` above an export counted; NaN floor always passed · fixed: only `/**` counts, invalid floor exits 2.
- `.gitignore`, `.dockerignore` `[correctness]` · scanner writes `.scannerwork/` into the checkout · fixed: ignored.
- `apps/importer/src/read-catalogue.ts` `[design]` · `byCodeUnit` could live in its own module · left: two callers, same module family.

## ⚪ Disagree / Intentional

- `apps/importer/src/read-catalogue.ts:47` `[design]` · `readBlock` appends to the caller's `errors` · kept: it is the single error list `readCatalogue` already built, in folder order; returning and merging lists adds code for the same result.
- `vitest.config.ts` `[design]` · `export default` · required by Vitest (eslint exception for config files).

## Per-dimension summary

- Design: no over-engineering; two Makefile tidy-ups. · Docs: one wrong contract, otherwise accurate. · Tests: suite trustworthy, one weak assertion. · Security: token never printed nor on a command line; stale-report hole closed. · Correctness: refactor preserves behaviour; `byCodeUnit` equals the default sort.
