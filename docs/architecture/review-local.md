# Local review — ohm-sweet-ohm (chore/3-tooling-and-ci)

- Date: 2026-10-09
- Commit: branch head before push
- Scope: branch diff main...HEAD (workspace, TypeScript, ESLint, Prettier, Vitest, markdownlint, CI and security workflows, Markdown fixes)
- Checks run: design · docs · security (Gitleaks, pnpm audit, workflow permissions and pinning) · correctness (`pnpm check`, actionlint). Tests: no production code yet.
- Verdict: ship as-is · Must 0 · Should 0 · Nice 1

## 🔴 Must Have

_None._

## 🟡 Should Have

_None._

## 🔵 Nice to Have

- `vitest.config.ts` `[tests]` · `passWithNoTests` is on because no package exists yet · Remove it once the first package with tests lands (issue #5).

## ⚪ Disagree / Intentional

- `.github/workflows/codeql.yml`, `.github/workflows/dependency-review.yml` `[security]` · Jobs skipped while the repository is private · The free plan offers code scanning and dependency review on public repositories only; `pnpm audit --audit-level high` in CI stands in until then, and both jobs start automatically once public.
- `pnpm-workspace.yaml` `[security]` · GHSA-vfj7-8cjw-p6xm ignored · No patched version exists; reached only through markdownlint-cli2 on the repository's own globs.
- Branch protection on `main` `[security]` · Not configured · Unavailable on a private repository on the free plan; added to the public release checklist.
- `typescript` 6.0.3 instead of 7.x `[design]` · typescript-eslint 8.71 supports TypeScript below 6.1 only; typed linting matters more than the native compiler for now.

## Per-dimension summary

- Design: flat tooling, no package before it is needed · Docs: README development section, Markdown lint fixes · Tests: N/A · Security: actions pinned by SHA, read-only permissions, Gitleaks active, audit gate · Correctness: `pnpm check` and actionlint pass
