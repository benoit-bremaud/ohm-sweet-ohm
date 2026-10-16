# Security

## Reporting

The repository is private; report anything to its owner directly.

## Continuous checks

| Check | Tool | Scope | Blocking |
| --- | --- | --- | --- |
| Secrets | Gitleaks (`gitleaks.yml`) | every commit, weekly | yes |
| Static analysis | CodeQL (`codeql.yml`) | TypeScript | yes |
| Dependencies | `pnpm audit --audit-level high` (`ci.yml`) | every package | yes |
| Dockerfile lint | Hadolint, `make lint-docker` (`docker-security.yml`) | `apps/api/Dockerfile`, `docker/renderer/Dockerfile` | yes, warnings included |
| Dockerfile misconfiguration | Trivy config, `make scan-docker-config` | the same two Dockerfiles | yes, HIGH and CRITICAL |
| Image vulnerabilities | Trivy image, `make scan-docker-image` | the API image, as deployed to Fly.io | yes, HIGH and CRITICAL with a fix available |

Not scanned: the renderer image (`docker/renderer`) runs only in CI and on the curator's machine,
never serves traffic, and is 1.8 GB of KiCad; its Dockerfile is linted and config-scanned, not
its image. Base images are bumped by Dependabot (`docker` ecosystem).

## Accepted findings

An accepted Hadolint finding is suppressed inline in the Dockerfile with a one-line reason. An
accepted Trivy finding goes in `.trivyignore.yaml` with `paths`, `expired_at` and a `statement`;
there is none today, so the file does not exist.

## Runtime

The API container runs as UID 1000 with no npm. Its code only reads the database, but it shares
the importer's credential, which can write and migrate; a read-only Neon role for the API is a
follow-up. Secrets live in Fly secrets and GitHub Actions secrets, never in the repository (see
`docs/deploy.md`).
