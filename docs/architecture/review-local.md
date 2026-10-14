# Local review — ohm-sweet-ohm (feat/15-db)

- Date: 2026-10-14
- Commit: branch head before push
- Scope: branch diff main...HEAD (`packages/db`, `Spec.toRaw` in the domain, TypeScript target, project log)
- Checks run: correctness, schema and security (independent code reviewer, the only reviewer since Codex is unavailable) · 9 integration tests on PostgreSQL 17 via Testcontainers · `pnpm check` (135 tests)
- Verdict: ship as-is · Must 0 · Should 0 · Nice 0

## 🔴 Must Have

_None._ Confirmed: save is one transaction, re-saving a parent with variants is safe, floats round-trip exactly, no SQL injection path, tests run on GitHub Actions.

## 🟡 Should Have

_None._ Applied: both reads in one repeatable-read snapshot; `key_components` shape-checked on read; whole-object round-trip tests for a root and a variant without source URL; tests for a variant saved before its parent, a stored cycle and malformed key components.

## 🔵 Nice to Have

_None._ Applied: `quantity` check constraint, specs grouped once with `Map.groupBy`, `TRUNCATE` cleanup, exact `@types/pg` pin, deterministic cycle error message.

## ⚪ Disagree / Intentional

- `packages/db/src/schema.ts` `[design]` · Row types written by hand · Kysely decision; drift is caught by the whole-object round-trip tests on a real PostgreSQL.

## Per-dimension summary

- Design: adapter outside the domain, domain rules re-checked on read · Docs: project log · Tests: 9 integration tests, behaviour-focused · Security: parameterised queries only, connection string never logged · Correctness: all review findings applied
