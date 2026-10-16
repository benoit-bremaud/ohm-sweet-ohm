# Local quality and security gate. GitHub Actions does not run on this account, so these targets
# are the CI: every tool runs from its official image pinned by tag and digest.
HADOLINT_IMAGE := hadolint/hadolint:v2.15.1@sha256:32dac94127fd60b7b7e3fbfc65e1383b9b5e25c9bfd7b8536de7a539fe68a12d
TRIVY_IMAGE := aquasec/trivy:0.76.0@sha256:2416d1f74045b57274df1a340eee6b510cacd73c66a6ccb8da092b117eb7d222
SEMGREP_IMAGE := semgrep/semgrep:1.178.0-nonroot@sha256:2124de200043ce3ded427d02e924ff3b59d017020614d28c2bb7ce6656bec5d4
GITLEAKS_IMAGE := zricethezav/gitleaks:v8.30.1@sha256:c00b6bd0aeb3071cbcb79009cb16a60dd9e0a7c60e2be9ab65d25e6bc8abbb7f
# Named registry rulesets: --config auto would send the project URL and is not reproducible.
# No p/secrets: Semgrep prints the matched value; gitleaks (scan-secrets) redacts it.
SEMGREP_RULES := --config p/javascript --config p/typescript --config p/nodejs
DOCKERFILES := apps/api/Dockerfile docker/renderer/Dockerfile
TRIVY_CACHE ?= $(HOME)/.cache/trivy
IMAGE ?= ohm-sweet-ohm-api

.PHONY: lint-docker scan-docker-config scan-docker-image build-api smoke-api sast scan-secrets \
	check-fast check-local

# Semgrep SAST, blocking on any finding. Rules are fetched from the registry (network needed);
# the engine is pinned. Exclusions live in .semgrepignore. The git directory is mounted at its own
# path so that git, and so .gitignore, also works from a worktree: untracked files are skipped.
GIT_COMMON_DIR = $(abspath $(shell git rev-parse --git-common-dir 2>/dev/null))
sast:
	@test -n "$(GIT_COMMON_DIR)" || { echo "sast: not a git checkout" >&2; exit 1; }
	docker run --rm --user "$$(id -u):$$(id -g)" -e HOME=/tmp -v "$(CURDIR)":/src:ro -w /src \
		-v "$(GIT_COMMON_DIR)":"$(GIT_COMMON_DIR)":ro \
		$(SEMGREP_IMAGE) semgrep scan $(SEMGREP_RULES) --metrics=off --disable-version-check \
		--error --quiet

# Secrets in the whole git history (git dir mounted as for sast, or a worktree scans 0 commits).
scan-secrets:
	@test -n "$(GIT_COMMON_DIR)" || { echo "scan-secrets: not a git checkout" >&2; exit 1; }
	docker run --rm --user "$$(id -u):$$(id -g)" -e HOME=/tmp -v "$(CURDIR)":/repo:ro \
		-v "$(GIT_COMMON_DIR)":"$(GIT_COMMON_DIR)":ro $(GITLEAKS_IMAGE) \
		detect --source /repo --no-banner --redact

# Run by the pre-push hook (.githooks/pre-push): the checks that take under a minute.
check-fast:
	pnpm check
	$(MAKE) sast scan-secrets

# The full gate, before every merge.
check-local: check-fast
	$(MAKE) lint-docker scan-docker-config build-api smoke-api scan-docker-image
	pnpm catalogue:render
	pnpm audit --prod

# The hadolint image has no ENTRYPOINT, only a CMD: the binary name is passed on purpose.
lint-docker:
	docker run --rm -v "$(CURDIR)":/repo:ro -w /repo $(HADOLINT_IMAGE) \
		hadolint --config .hadolint.yaml $(DOCKERFILES)

# Only the Dockerfile scanner: IaC added later must opt in instead of failing this target.
# node_modules holds third-party Dockerfiles (test fixtures of some packages) that are never built.
scan-docker-config:
	mkdir -p "$(TRIVY_CACHE)"
	docker run --rm --user "$$(id -u):$$(id -g)" -e TRIVY_MISCONFIG_SCANNERS=dockerfile \
		-e TRIVY_CACHE_DIR=/cache -v "$(TRIVY_CACHE)":/cache -v "$(CURDIR)":/repo:ro -w /repo \
		$(TRIVY_IMAGE) config --severity HIGH,CRITICAL --exit-code 1 \
		--skip-dirs node_modules,build,.wrangler .

build-api:
	docker build -f apps/api/Dockerfile -t $(IMAGE) .

# Proves the bundle starts and answers /health as the unprivileged user; the database URL points
# nowhere on purpose, the health route does not need it.
smoke-api:
	docker rm -f osh-api-smoke >/dev/null 2>&1 || true
	docker run -d --name osh-api-smoke -e DATABASE_URL=postgres://nobody:nothing@127.0.0.1:1/nothing $(IMAGE) >/dev/null
	for i in $$(seq 1 20); do \
	  status="$$(docker inspect -f '{{.State.Health.Status}}' osh-api-smoke)"; \
	  if [ "$$status" = healthy ]; then docker rm -f osh-api-smoke >/dev/null; echo "healthy after $$i s"; exit 0; fi; \
	  sleep 1; \
	done; \
	docker logs osh-api-smoke; docker rm -f osh-api-smoke >/dev/null; echo "not healthy after 20 s"; exit 1

scan-docker-image:
	mkdir -p "$(TRIVY_CACHE)"
	docker run --rm --user "$$(id -u):$$(id -g)" --group-add "$$(stat -c %g /var/run/docker.sock)" \
		-e TRIVY_CACHE_DIR=/cache -v "$(TRIVY_CACHE)":/cache \
		-v /var/run/docker.sock:/var/run/docker.sock \
		$(TRIVY_IMAGE) image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 $(IMAGE)
