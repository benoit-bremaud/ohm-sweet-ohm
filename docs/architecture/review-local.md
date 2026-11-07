# Local review — ohm-sweet-ohm (ci/68-local-ci-prod-only)

- Date: 2026-11-07
- Commit: `0bc475a` reviewed (round 1); fixes in `db8ddd1` (round 2) and `55e2817` (round 3)
- Scope: branch diff origin/main (`79e399b`)...HEAD — local CI (just, lefthook, mise, attestation), `prod.yml` as the only workflow, seven workflows and the Makefile removed, dependency security bumps, Node 22.23.4, repository made public
- Checks run: adversarial (Opus, 2 rounds) · design · docs · tests · containers · security + correctness (six read-only reviewers, reconciled)
- Verdict: fix Must Have first (done in `db8ddd1`) · Must 3 · Should 14 · Nice 9 · Disagree 6

## Adversarial review (#236)

- Round 1 on `0bc475a`: Must 3 · Should 11 · Nice 7 · unverified 0 · Push gate: closed
- Round 2 on `db8ddd1`: 3 Must + 8 Should + 2 Nice fixed · 0 not fixed · 0 regressed · new Must 2 (stale `catalogue:render` comment in `apps/importer/src/main.ts`, `deploy.sh` header contradicting the code) · Push gate: closed
- Round 3 on `55e2817`: 2 Must + 2 Should + 2 Nice fixed · 0 not fixed · 0 regressed · new Must 0 · **Push gate: open**
- Hosted reviewers (filled at the pre-merge run): Copilot not requested (project decision, 2026-10-14) · Codex `@codex review` optional

## Pre-merge gate (head SHA `55e2817`, `--push` mode)

| Step | Result |
| --- | --- |
| 0 CI mirror | n/a — no workflow runs on `pull_request` any more; `prod.yml` (tag) rehearsed by `just rehearse` (stable, prerelease, refused: ok) |
| 1 Tests | ✅ 234 unit/integration (16 files, Vitest, Testcontainers) · ✅ 41 local-CI wiring cases · ✅ 22 attestation cases · E2E/smoke: step 5 |
| 2 Coverage | tests 95.53 % stmts / 93.90 % branches / 95.12 % funcs / 95.98 % lines (floor 80) · docs 100 % (78/78, floor 90) |
| 3 SonarQube | ⏸ deferred to the pre-merge run (`--push`) |
| 4 Secrets | ✅ gitleaks clean (origin/main..HEAD and the 44-commit history) · no tracked `.env*` · diff read: only secret names (`FLY_API_TOKEN`, `DATABASE_URL`), one signing e-mail in `.github/allowed_signers` |
| 5 E2E/smoke | ⏸ deferred to the pre-merge run (`just gate`: API image smoke, Trivy image, render); QA pass on staging after the merge |

- Gate: `--push`: **pre-push green** — `mise x -- just check` passed on `db8ddd1` and `55e2817` (2 min 40) (lint, tests, coverage, Semgrep, `pnpm audit --audit-level high` 0 high, gitleaks); SonarQube, image smoke, Trivy image, render, attestation deferred to `just gate` on the pushed head. The first merge cannot use `just merge` (`.github/allowed_signers` reaches `origin/main` with this PR): `gh pr merge` with the recorded waiver, then `just gate` on `main`.

## 🔴 Must Have

- `justfile:71-73`, `SECURITY.md:17`, `PROJECT_LOG.md` `[adversarial]` · `pnpm audit --prod` audited less than the former `ci.yml` (no dev dependencies, 2 high in `markdown-it` 15.0.1), and Trivy fs cannot see pnpm dev dependencies, so the fallback the log named did not exist · **fixed**: `pnpm audit --audit-level high`, `pnpm.overrides` `markdown-it` 15.0.3, scope corrected in SECURITY.md, docs/deploy.md and the log
- `docs/architecture/decisions/0004-staging-hosting.md:134-145` `[adversarial|docs]` · the decision outcome still described a workflow on every merge and a GitHub `DATABASE_URL` secret, while `docs/deploy.md` and the component diagram cite it · **fixed**: dated "Amended 2026-11-07 (#68)" section; ADR-0002 wording ("in CI") reworded; `03-component.md` subgraph renamed "Curator machine"
- `docs/WORKPLAN.md:19,42,111-114` `[adversarial|docs]` · "single private repo", CI baseline with CodeQL and dependency review, M5 "import runs in CI", "then repo goes public" · **fixed**: public since 2026-11-07, local checks, rulesets on `main` and `v*` as the M5 item

## 🟡 Should Have

- `justfile:86-109` `[adversarial]` · the gate attested whatever HEAD was at its end, not the commit it checked · **fixed**: `check` runs from the body after `start=$(git rev-parse HEAD)`, refused when HEAD moved
- `lefthook.yml:35-38` `[adversarial]` · pre-push lost the dirty-tree guard of the old hook · **fixed**: `git diff --quiet HEAD --` first
- `justfile:233-236` `[adversarial|containers]` · `mise outdated` reports nothing for exact pins; no recurring Trivy scan since `docker-security.yml` went · **fixed**: `mise outdated --bump`, Trivy fs and image in `nightly`
- `README.md:17-22` `[adversarial|docs]` · `just setup` fails on a fresh clone (`just` comes from mise, `mise trust` needed) · **fixed**
- `justfile:172` `[adversarial]` · any act failure counted as "refused" · **fixed**: the log must say "not a release tag"
- `scripts/deploy.sh:33-37` `[adversarial|security|design]` · a stray shell `DATABASE_URL` beat `.env.staging`; quoted values kept their quotes · **fixed**: the file always, quotes and `\r` stripped
- `justfile:191` `[design]` · `just deploy staging v1.2.3` ignored the tag silently · **fixed**: refused
- `package.json:20-21` `[design]` · dead `pnpm check` (second, weaker L1) and `catalogue:render` duplicating `just render` · **fixed**: removed, README points at `just render`
- `package.json:9`, `.npmrc` `[security|adversarial]` · `engines` floor below Astro's need; no `engine-strict` · **fixed**: `^22.23.4`, `engine-strict=true`
- `scripts/systemd/ohm-sweet-ohm-nightly.service:9` `[adversarial|docs|security]` · nightly runs in the main checkout, ESLint linted 112 files of other sessions' worktrees; no install procedure · **partly fixed**: `.claude/` ignored by ESLint, install lines in `docs/deploy.md`; a detached worktree of `origin/main` is #71
- `scripts/test-local-ci.sh:49-54` `[tests]` · the refusals ran the real `deploy.sh` with `flyctl` on PATH and asserted only the `deploy:` prefix · **fixed**: stub `flyctl` and `pnpm`, reason asserted, "nothing called" asserted
- `scripts/test-attest.sh:94,189` `[tests]` · `release` stdout check satisfied by stderr; the signature check itself never failed in a test · **fixed**: bare-SHA stdout assertion, trusted key over a wrong payload refused ("bad signature")
- `.github/workflows/prod.yml:39-72` `[security]` · a `v*` tag pushed from a branch runs that branch's `prod.yml` with `FLY_API_TOKEN` · **follow-up #69**: tag ruleset on `v*` and a `production` environment holding the secret (available now that the repository is public)
- `docs/deploy.md:157` `[adversarial]` · the one-at-a-time Trivy config command differed from the gate's (scanned `node_modules`) · **fixed**: same flags as the gate

## 🔵 Nice to Have

- `apps/api/Dockerfile:1`, `docker/renderer/Dockerfile:1` `[containers]` · floating `# syntax=docker/dockerfile:1`, no `# check=error=true`, no `docker build --check`; renderer without a documented `HEALTHCHECK` exemption · #42
- `justfile:103` `[containers]` · SBOM as unversioned `spdx-json`; CycloneDX 1.5 with a coverage assertion preferred · #42
- `.github/dependabot.yml:4-9` `[containers]` · no `groups` for the docker ecosystem · #42
- `justfile:198-230` `[design]` · "HEAD is up-to-date origin/main" written three times (from the `local-ci` template) · upstream: a private `on-main` recipe in the template
- `scripts/attest.sh:2,87`, `scripts/test-attest.sh:2`, `scripts/check-commit-msg.sh:2` `[adversarial|docs]` · bare "ADR-0003/0004" and foreign issue numbers read as local ones · upstream (vendored copies stay byte-identical to `~/.claude/scripts`)
- `scripts/test-local-ci.sh:47` `[tests|design|adversarial]` · `n=$((n + 10))` hand count for the static greps · kept (cheap greps, duplicates of actionlint/zizmor; trim rather than extend)
- `justfile` `deploy`/`merge` `[tests]` · no behavioural test of the recipes (dirty tree, not on main, prod trap, `--match-head-commit`) · #72
- `scripts/check-commit-msg.sh:36` `[security]` · `${#subject}` may count bytes under some shells · upstream
- `packages/db/src/block-repository.ts:57` `[adversarial]` · comment "two CI jobs" out of date · follow-up with the next db change

## ⚪ Disagree / Intentional

- `.github/allowed_signers:1` `[security|adversarial]` · the work e-mail as signer principal · a label for `find-principals`, the owner's convention across repositories (brasse-bouillon), recorded in PROJECT_LOG
- `scripts/deploy.sh:19-20` `[design]` · the environment argument changes nothing for `api` today · the skill's call shape (`deploy.sh <component> <env>`), real once the second Fly app exists
- `justfile:68` `[adversarial]` · osv-scanner dropped from L1 · recorded owner decision; only the parity claims were a Must (fixed)
- Hadolint and Trivy "absent in CI" `[containers]` · local tiers plus attestation replace CI by design (skill `local-ci`, agents-skills ADR-0003/0004), recorded in SECURITY.md
- `codeql.yml`, `dependency-review.yml` deleted `[adversarial]` · skill `local-ci` rule 4 and agents-skills ADR-0004
- Staging and prod on one Fly app and one Neon project `[security|design|adversarial]` · derogation recorded (PROJECT_LOG 2026-11-07, MCDA 435/415/325); the second app (#70) is the follow-up that gives the promotion chain its meaning

## Per-dimension summary

- Adversarial: 3 Must (audit scope, ADR-0004, WORKPLAN) and 11 Should, all fixed or filed; `just check`, `rehearse`, Trivy config and the base-image digest verified clean · Design: no Must; two Makefile leftovers removed, the `env` argument and the template duplication noted · Docs: in-scope files accurate; stale CI/private statements in neighbouring docs fixed · Tests: `test-attest.sh` close, `test-local-ci.sh` gained stubs and reasons; recipe-level behavioural tests filed · Containers: runtime image meets the mandatory set; nightly Trivy added; build checks and SBOM format filed · Security: no Must; tag-trigger trust and `FLY_API_TOKEN` environment filed; `prod.yml` pins, permissions and tag handling clean
