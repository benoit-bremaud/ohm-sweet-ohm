# Local review — ohm-sweet-ohm (feat/14-domain)

- Date: 2026-10-14
- Commit: branch head before push
- Scope: branch diff main...HEAD (`packages/domain`, project log)
- Checks run: correctness and design (independent code reviewer against 04-class.md and the parameter spec) · tests (43 domain tests, mutation check on the finite-number guard) · `pnpm check` · security (no I/O, no dependency)
- Verdict: ship as-is · Must 0 · Should 0 · Nice 1

## 🔴 Must Have

_None._ Review found 1 Must: a NaN or infinite value made `Catalogue.publish` throw; fixed, and the new test fails when the guard is removed.

## 🟡 Should Have

_None._ Applied: blank change summary counts as missing; clear message for a missing range end; duplicate enum values refused; invariant tests added (second root from a variant, in-place root republication, moving a childless block across base circuits, unknown base circuit with a known parent, moving a subtree, first-level relink).

## 🔵 Nice to Have

- `packages/domain/src/specs.ts` `[design]` · A raw spec mixing `text` with `min`/`max` is accepted on its typed part · The `meta.yaml` reader never produces that shape; revisit if another input channel appears.

## ⚪ Disagree / Intentional

- `packages/domain/src/catalogue.test.ts` `[tests]` · Full error-field order asserted in one test · The order is deterministic and part of what curators read.
- Reviewer finding "no count rejection tests" `[tests]` · Already covered in `specs.test.ts` (zero, non-integer, count with a unit, measure without unit).

## Per-dimension summary

- Design: matches 04-class.md for M1 scope · Docs: project log · Tests: 43 domain tests, behaviour-focused · Security: pure domain · Correctness: every publication invariant tested
