# Local review — ohm-sweet-ohm (spike/6-kicad-render)

- Date: 2026-10-10
- Commit: branch head before push
- Scope: branch diff main...HEAD (renderer Dockerfile, render script, catalogue workflow, ADR-0002, project log)
- Checks run: correctness (script run end to end in the renderer image; shellcheck; actionlint) · security (image pinned by digest, actions pinned by SHA, read-only permissions, Gitleaks, SVG content check) · docs · `pnpm check`. Tests: shell script exercised end to end; no unit test (spike).
- Verdict: ship as-is · Must 0 · Should 0 · Nice 1

## 🔴 Must Have

_None._

## 🟡 Should Have

_None._

## 🔵 Nice to Have

- `.github/workflows/catalogue.yml` `[ci]` · The renderer image is rebuilt on each run (about 1 minute) · Publish it to a registry if catalogue changes become frequent.

## ⚪ Disagree / Intentional

- `docker/renderer/Dockerfile` `[security]` · Inkscape (GPL) in the image · CI tool producing files only, never distributed with the MIT code (ADR-0002).
- ERC not run in CI `[correctness]` · Out of the spike's scope; the ERC gating item of the tooling backlog records the library-table finding.

## Per-dimension summary

- Design: rendering kept outside the domain, one derived image · Docs: ADR-0002 with measurements · Tests: end-to-end run in the image · Security: pinned image and actions, minimal permissions · Correctness: shellcheck, actionlint and `pnpm check` pass
