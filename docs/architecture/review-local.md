# Local review — ohm-sweet-ohm (feat/17-api)

- Date: 2026-10-15
- Commit: branch head before push
- Scope: branch diff main...HEAD (`apps/api`, `packages/schemas` response schema, `packages/db` version, schematic lookup and pool error callback, importer wiring, sequence diagram, README, project log)
- Checks run: correctness, security and design against `05-sequence-inspect-block.md` (independent code reviewer, the only reviewer) · 177 tests including PostgreSQL integration tests and a mutation check · end-to-end smoke test (render, import, curl, database outage, SIGTERM) · `pnpm check`
- Verdict: ship as-is · Must 0 · Should 0 · Nice 0

## 🔴 Must Have

_None._ Found by the smoke test before review and fixed: a dropped database connection crashed the API (unhandled pool error event).

## 🟡 Should Have

_None._ Applied: unknown routes answer the documented `{ error }` shape; `If-None-Match` follows RFC 9110 weak comparison (lists, `W/` tags, `*`).

## 🔵 Nice to Have

_None._ Applied: clean shutdown on SIGTERM and SIGINT (verified, exit code 0).

## ⚪ Disagree / Intentional

- `apps/api/src/main.ts` `[design]` · The pool error callback refers to `app` declared later · It can only fire after a connection was opened, which happens after `buildApp` returns.

## Per-dimension summary

- Design: matches the sequence diagram; the API never runs migrations · Docs: diagram, README, project log · Tests: cache unit tests with a fake clock and source, route tests with `inject`, integration test on PostgreSQL · Security: inert SVG headers, slug validation, server errors never expose their cause · Correctness: outage behaviour verified live
