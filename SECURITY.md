# Security

## Reporting

The repository is public (ADR-0005 of agents-skills, 2026-11-07); report a vulnerability privately to its owner (`bbd.concept@gmail.com`), never in a public issue.

## Continuous checks

Every check runs locally (skill `local-ci`, `docs/deploy.md` § Local CI): `just check` on every
push, `just gate` before every merge, `just nightly` on a timer. No GitHub workflow is left
(ADR-0005).

| Check | Tool | Scope | Blocking |
| --- | --- | --- | --- |
| Secrets | gitleaks (`just secrets`; staged files on commit) | the whole git history, every push | yes |
| Static analysis | Semgrep Community Edition (`just security`) | `p/javascript`, `p/typescript`, `p/nodejs` on the shipped code and the scripts | yes |
| Dependencies | `pnpm audit --audit-level high` (`just security`); Trivy fs (`just gate`, `just nightly`) adds the production lockfile | every package, dev dependencies included | yes, HIGH and CRITICAL |
| Dockerfile lint | Hadolint (`just lint`) | `docker/renderer/Dockerfile` | yes, warnings included |
| Dockerfile misconfiguration | Trivy config (`just gate`) | the same Dockerfile | yes, HIGH and CRITICAL |
| Filesystem vulnerabilities | Trivy fs (`just gate`, `just nightly`) | the repository | yes, HIGH and CRITICAL |
| Deep secret history | TruffleHog, offline (`just nightly`) | the whole git history | yes |
| Toolchain drift | `mise outdated --bump` (`just nightly`) | `mise.toml` pins | no, report only |

Not scanned: the renderer image (`docker/renderer`) runs only in the gate and on the curator's machine,
never serves traffic, and is 1.8 GB of KiCad; its Dockerfile is linted and config-scanned, not
its image. Base images are bumped by Dependabot (`docker` ecosystem).

## Accepted findings

An accepted Hadolint finding is suppressed inline in the Dockerfile with a one-line reason. An
accepted Trivy finding goes in `.trivyignore.yaml` with `paths`, `expired_at` and a `statement`.
One today: picomatch CVE-2026-112366 (GHSA-fc5q-39xc-vjpf, #112, #131), scoped to `pnpm-lock.yaml`,
expiring 2027-02-18. `just gate` and `just nightly` pass the file with `--ignorefile`, so it stays
in place, with `vulnerabilities: []` when it holds no entry.

## Runtime

There is no deployed container: the Worker reads the database directly through Hyperdrive. Its code
only reads, but it shares the importer's credential, which can write and migrate; a read-only Neon
role for the Worker is a follow-up. The connection string lives in the git-ignored `.env.staging`
on the curator's machine and in the Hyperdrive config at Cloudflare, never in the repository (see
`docs/deploy.md`).
