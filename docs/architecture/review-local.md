# Local review — ohm-sweet-ohm (feat/16-importer)

- Date: 2026-10-14
- Commit: branch head before push
- Scope: branch diff main...HEAD (sequence diagram, `packages/db` mirror and migration 0002, `apps/importer`, root scripts, README, project log, untracked build file)
- Checks run: correctness and design against `02-sequence-publish-blocks.md` (independent code reviewer, the only reviewer) · 28 importer and database tests (Testcontainers) with a mutation check · end-to-end smoke test (Docker render, two imports, empty folder refused) · `pnpm check`
- Verdict: ship as-is · Must 0 · Should 0 · Nice 0

## 🔴 Must Have

_None._ Confirmed: parents written before variants, removals last in one statement, rollback on failure.

## 🟡 Should Have

_None._ Applied: symbolic links followed (silent skip then deletion — mutation-checked test); "missing meta.yaml" message; publication in waves with parent-cycle errors; mirror tests for re-parenting with removal, changed parent with unchanged variants and spec-order hash stability; advisory lock serialising concurrent mirrors.

## 🔵 Nice to Have

_None._ Applied: locale-independent spec sort in the hash and a note on key order; friendly CLI error on a wrong path; diagram aligned with the code; dead code and weak assertions in tests fixed; migration note on pre-existing empty hashes.

## ⚪ Disagree / Intentional

- `apps/importer/src/import-catalogue.ts` `[design]` · A failed parent also reports its variants with "unknown parent" · The curator sees the root cause first in the list; filtering would hide independent errors.

## Per-dimension summary

- Design: matches the sequence diagram; rendering stays outside the importer · Docs: diagram, README, project log · Tests: unit tests with a fake repository, integration tests on PostgreSQL · Security: parameterised queries, advisory lock · Correctness: all review findings applied, smoke-tested end to end
