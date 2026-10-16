# Local review — ohm-sweet-ohm (feat/19-deploy)

- Date: 2026-10-15
- Commit: `e41e817` (branch head before push)
- Scope: branch diff main...HEAD (API image and Fly manifest, three workflows, Makefile, ADR-0004, deployment view, `docs/deploy.md`, `SECURITY.md`, `wrangler.jsonc`)
- Checks run: design · docs · tests · security · correctness (five independent read-only reviewers, reconciled) · `pnpm check` green under Node 22.23.3, image built, started and scanned locally
- Verdict: fix Must Have first · Must 1 · Should 10 · Nice 6
- Outcome (same day, before push): the Must and every Should applied in the follow-up commit; the Nice items filed as issues (owner decision); four findings disagreed with evidence.

## 🔴 Must Have

- `apps/web/wrangler.jsonc:10-15` `[correctness]` · Branch previews (`wrangler preview`, run by Workers Builds) do not inherit the top-level `vars` and the command refuses to run without a `previews` block, so every preview would start without `API_URL` and answer 500: the M1 "done when" itself. `preview_urls` governs Version URLs, not previews, and is true by default. · Applied: `previews.vars.API_URL` added, `preview_urls` removed; `wrangler deploy --dry-run` shows the variable.

## 🟡 Should Have

- `.github/workflows/catalogue.yml:59` `[docs][security][correctness]` · `if: github.event_name != 'pull_request'` let a `workflow_dispatch` from any branch import that branch's catalogue into the shared staging database, against the comment next to it. · Applied: `if: github.ref == 'refs/heads/main'`.
- `.github/workflows/catalogue.yml:26-28` `[security][correctness]` · Workflow-level `cancel-in-progress: true` cancelled a running import on `main` when a second push landed (the job-level setting could not override it). · Applied: `cancel-in-progress: ${{ github.event_name == 'pull_request' }}`, redundant job-level block removed.
- `.github/workflows/docker-security.yml:4-14` `[tests]` · No pull request built the bundle when only `apps/api/src` or `packages/` changed; the artefact first ran on `main`. · Applied: `apps/api/**` and `packages/**` in the path filters, `make smoke-api` (container healthy) in the image job.
- `deploy-api.yml` × `catalogue.yml` `[design]` · Migrations run in the importer only, so a merge that adds one may redeploy the API minutes before the schema changes. · Applied: documented in the deployment view, ADR-0004 and `docs/deploy.md`; a Fly `release_command` is the fix if it ever bites.
- `package.json#packageManager` `[security]` · `corepack enable` downloaded pnpm at image build without an integrity check. · Applied: `pnpm@10.30.3+sha512.…` written by `corepack use`.
- `.github/dependabot.yml` `[security]` · Only the `docker` ecosystem: SHA-pinned actions and npm packages would never move. · Applied: `github-actions` and a grouped weekly `npm` entry.
- `docs/deploy.md:63-64` `[security]` · `flyctl secrets set DATABASE_URL='…'` and a printed deploy token put secrets in the shell history and terminal. · Applied: stdin forms documented (`secrets import < .env.staging`, `… | gh secret set`), which is what was actually done.
- `apps/api/fly.toml:10` `[correctness]` · `kill_timeout = "10s"` was short for `app.close()` plus `db.destroy()` during a catalogue reload. · Applied: 30 s.
- `apps/api/Dockerfile:56` `[correctness]` · HEALTHCHECK hard-coded port 3000 while `PORT` is overridable. · Applied: `process.env.PORT`.
- `docs/deploy.md:12-13`, ADR-0004 lines 129 and 139, `SECURITY.md:30` `[docs]` · "every push to `main`" ignored the path filters; "deployment README" pointed nowhere; the import trigger list missed the packages and lockfile; "only reads the database" hid that the API shares the importer's writable credential. · Applied: wording fixed; read-only Neon role filed as a follow-up.

## 🔵 Nice to Have

- `apps/api/fly.toml:16-18` `[design]` · `[env]` repeats the Dockerfile's `ENV`. · Filed (issue).
- `.github/workflows/docker-security.yml:45-48` `[correctness]` · Both jobs save under the same cache key, the second logs a warning; `restore-keys` still serves a rolling cache. · Filed (issue).
- `apps/api/Dockerfile:16-23` `[design][correctness]` · Workspace manifests listed by hand; a new package fails loudly (`--frozen-lockfile`), `pnpm fetch` would remove the list. · Filed (issue).
- `Makefile:30`, `docs/deploy.md` `[docs]` · Comment on the Docker socket mount; `host.docker.internal` needs `--add-host` on Linux (the example now uses `--env-file .env.staging`). · Filed (issue).
- `apps/api/src/main.ts:13` `[correctness]` · Pre-existing (#17): the pool's error callback references `app` before it is assigned; a pool error during `buildApp` would throw a `ReferenceError`. · Filed (issue).
- `.github/workflows/deploy-api.yml:36` `[tests]` · No `curl` of the public URL after the deploy; the Fly health check already gates the release. · Not applied.

## ⚪ Disagree / Intentional

- `docs/deploy.md:78` `[docs][security]` · "`npx wrangler preview` is not a current command": `wrangler preview --help` answers in wrangler 4.151 (open beta) and it is the default Preview command of Workers Builds in Cloudflare's documentation. Kept.
- `apps/api/build.ts` `[security]` · Source map shipped in the image: not served by Fastify, repository private; to revisit at publication.
- `Makefile:30` `[correctness]` · `stat -c %g` is GNU-only: the only machine is Linux and CI runs Ubuntu.
- `.github/workflows/docker-security.yml` `[design]` · YAML anchors for the two path lists: two occurrences, under the rule of three.

## Per-dimension summary

- Design: no over-engineering; two couplings named (hand-listed manifests, importer-owned migrations), the second documented · Docs: six stale sentences fixed, one false Must refuted with the binary · Tests: no test to add; the artefact smoke test in CI was the one real gap · Security: nothing committed, forks cannot reach secrets, hardening checklist met; pnpm integrity pin, Dependabot scope and secret-handling docs tightened · Correctness: the previews block was the only blocking defect; the bundle plugin, `.dockerignore`, layer order, Fly paths and the artifact round-trip were verified correct.
