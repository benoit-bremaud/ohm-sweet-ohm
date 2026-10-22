# Local review — ohm-sweet-ohm (fix/27-pool-error-callback)

- Date: 2026-10-22
- Commit: `26e0b69` reviewed; fixes applied in the next commit
- Scope: branch diff main...HEAD (shared pino logger created before the pool, `idleConnectionErrorHandler`, `buildApp` takes a `FastifyBaseLogger`, `pino` dependency)
- Checks run: design · docs · tests · security + correctness (four read-only reviewers, reconciled)
- Verdict: no Must Have · Must 0 · Should 2 · Nice 2 · Disagree 1
- Outcome (same day, before push): both Shoulds and both Nice applied; one Disagree.

## Pre-merge gate (head SHA: the fix-up commit on top of `26e0b69`)

| Step        | Result                                                                                                                          |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------- |
| 1 Tests     | ✅ 234 unit/integration (`make check-local`) · ✅ `smoke-api` on the built Docker image                                         |
| 2 Coverage  | tests 95.53 % stmts / 93.9 % branches / 95.12 % funcs / 95.98 % lines (floor 80) · docs 100 % (78/78, floor 90)                 |
| 3 SonarQube | ✅ PASSED                                                                                                                       |
| 4 Secrets   | ✅ gitleaks clean (`origin/main..HEAD`) · no tracked `.env` · diff read: nothing sensitive                                      |
| 5 QA pass   | ✅ no UI: `smoke-api` starts the real image and hits the routes; request logging checked by the new `buildApp logger` unit test |

- Gate: **GREEN — merge authorised**

## 🔴 Must Have

_None._

## 🟡 Should Have

- `pnpm-lock.yaml` `[design|security]` · `pnpm add` re-resolved an unrelated optional peer (`@emnapi/core` 1.11.3 → 1.11.1) and duplicated `@astrojs/compiler-*` snapshots · applied: lockfile restored from `main`, only the `pino` importer entry added (+3 lines), `pnpm install --frozen-lockfile` passes.
- `apps/api/src/app.ts:52` `[tests]` · the injected-logger branch of `buildApp` was untested · applied: `app.test.ts` `buildApp logger` test injects a pino instance with a capturing stream and asserts the request line carries `req.url`.

## 🔵 Nice to Have

- `apps/api/src/logger.ts` `[design]` · the module name said "logger" but holds the pool callback · applied: renamed `pool-error-handler.ts`.
- `apps/api/src/pool-error-handler.ts:3` `[docs]` · docstring gave the why, not the contract · applied: "logs at warn and never rethrows".

## ⚪ Disagree / Intentional

- `apps/api/src/main.ts:17` `[correctness]` · claim: a bare `pino()` passed as `loggerInstance` loses Fastify's `req`/`res`/`err` serializers · not so: Fastify 5.12.7 `lib/logger-factory.js:97-101` wraps the instance in a child with its own serializers merged; the new test sees `req.url` in the request log.
- `apps/api/src/pool-error-handler.test.ts` `[tests]` · the unit test pins the callback contract, not the TDZ itself (that lives in `main.ts`, excluded from coverage and covered by `smoke-api`); a `not.toThrow` assertion would be tautological, so none was added.

## Per-dimension summary

- Design: correct fix, no over-engineering; lockfile noise removed · Docs: 100 %, fresh · Tests: callback and logger injection covered · Security: nothing new; single pino copy, not bundled (esbuild externals) · Correctness: no bug found.
