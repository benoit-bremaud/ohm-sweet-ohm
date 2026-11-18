# Local review — ohm-sweet-ohm (fix/131-trivy-picomatch-waiver)

Pre-push review of the Trivy waiver for the picomatch advisory of issue #131.

- Date: 2026-11-18
- Commit: b552d5d
- Scope: branch diff `origin/main...HEAD`
- Checks run: adversarial (fresh reviewer, 3 rounds) · tests · security
- Verdict: ship · Must 0 · Should 0 · Nice 0

## Adversarial review (#236)

- Round 1 on `f957ef4`: Must 1 (stale `SECURITY.md`) · Should 2 (missing file is fatal; no wiring test) · Nice 3 · Push gate: closed.
- Round 2 on `caeb3fe`: Must fixed · Should 1 partially fixed · Nice 2 · Push gate: open.
- Round 3 on `b552d5d`: all fixed · no new finding · **Push gate: open**.
- Optional second review (owner's own account): not run (never a gate step).

## Pre-merge gate (head SHA b552d5d)

| Step | Result |
| --- | --- |
| 0 CI mirror | n/a — no PR workflow (local CI only) |
| 1 Tests | ✅ `just check` exit 0 · test-local-ci 47 cases |
| 2 Coverage | ⏸ deferred to the pre-merge run (`--push`) |
| 3 SonarQube | ⏸ deferred to the pre-merge run (`--push`) |
| 4 Secrets | ✅ gitleaks clean · no tracked .env · diff read: nothing sensitive |
| 5 E2E/smoke | ⏸ deferred to the pre-merge run (`--push`) |

- Gate: **pre-push green** — `trivy fs` exits 1 without the ignore file, 0 with it.

## 🔴 Must Have

_None._

## 🟡 Should Have

_None._

## 🔵 Nice to Have

_None._

## ⚪ Disagree / Intentional

- `justfile:107` `[adversarial]` · `trivy config` and `trivy image` keep no ignore file · the waiver covers a lockfile finding only; the API image holds no HIGH or CRITICAL finding.

## Per-dimension summary

- Adversarial: 3 rounds, gate open · Tests: wiring and required fields of the ignore file checked · Security: waiver scoped to `pnpm-lock.yaml`, expires 2027-02-18, same justification as the pnpm audit waiver of #112.
