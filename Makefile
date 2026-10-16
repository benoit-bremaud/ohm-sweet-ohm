# Container security tooling, run from the official images pinned by tag and digest so local
# runs and CI (.github/workflows/docker-security.yml) apply the same rules.
HADOLINT_IMAGE := hadolint/hadolint:v2.15.1@sha256:32dac94127fd60b7b7e3fbfc65e1383b9b5e25c9bfd7b8536de7a539fe68a12d
TRIVY_IMAGE := aquasec/trivy:0.76.0@sha256:2416d1f74045b57274df1a340eee6b510cacd73c66a6ccb8da092b117eb7d222
DOCKERFILES := apps/api/Dockerfile docker/renderer/Dockerfile
TRIVY_CACHE ?= $(HOME)/.cache/trivy
IMAGE ?= ohm-sweet-ohm-api

.PHONY: lint-docker scan-docker-config scan-docker-image build-api smoke-api

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
