# Security

## Reporting

The repository is private; report anything to its owner directly.

## Continuous checks

Every check runs locally (skill `local-ci`, `docs/deploy.md` § Local CI): `just check` on every
push, `just gate` before every merge, `just nightly` on a timer. GitHub Actions only deploys a
signed release tag (`prod.yml`).

| Check | Tool | Scope | Blocking |
| --- | --- | --- | --- |
| Secrets | gitleaks (`just secrets`; staged files on commit) | the whole git history, every push | yes |
| Static analysis | Semgrep Community Edition (`just security`) | `p/javascript`, `p/typescript`, `p/nodejs` on the shipped code and the scripts | yes |
| Dependencies | `pnpm audit --prod --audit-level high` and osv-scanner on the lockfile (`just security`) | every package | yes |
| Dockerfile lint | Hadolint (`just lint`) | `apps/api/Dockerfile`, `docker/renderer/Dockerfile` | yes, warnings included |
| Dockerfile misconfiguration | Trivy config (`just gate`) | the same two Dockerfiles | yes, HIGH and CRITICAL |
| Filesystem vulnerabilities | Trivy fs (`just gate`) | the repository | yes, HIGH and CRITICAL |
| Image vulnerabilities | Trivy image (`just gate`) | the API image, as deployed to Fly.io, plus a Syft SBOM | yes, HIGH and CRITICAL with a fix available |
| Workflow hygiene | actionlint, zizmor (`just lint`); act rehearsal of a changed workflow (`just gate`) | `.github/workflows/prod.yml` | yes |
| Deep secret history | TruffleHog, offline (`just nightly`) | the whole git history | yes |

Not scanned: the renderer image (`docker/renderer`) runs only in the gate and on the curator's machine,
never serves traffic, and is 1.8 GB of KiCad; its Dockerfile is linted and config-scanned, not
its image. Base images are bumped by Dependabot (`docker` ecosystem).

## Accepted findings

An accepted Hadolint finding is suppressed inline in the Dockerfile with a one-line reason. An
accepted Trivy finding goes in `.trivyignore.yaml` with `paths`, `expired_at` and a `statement`;
there is none today, so the file does not exist.

## Runtime

The API container runs as UID 1000 with no npm. Its code only reads the database, but it shares
the importer's credential, which can write and migrate; a read-only Neon role for the API is a
follow-up. Secrets live in Fly secrets, the git-ignored `.env.staging` on the curator's machine and
one GitHub repository secret (`FLY_API_TOKEN`, for `prod.yml`), never in the repository (see
`docs/deploy.md`).
