# Container security tooling, run from the official images pinned by tag and digest so local
# runs and CI (.github/workflows/docker-security.yml) apply the same rules.
HADOLINT_IMAGE := hadolint/hadolint:v2.15.1@sha256:32dac94127fd60b7b7e3fbfc65e1383b9b5e25c9bfd7b8536de7a539fe68a12d
TRIVY_IMAGE := aquasec/trivy:0.76.0@sha256:2416d1f74045b57274df1a340eee6b510cacd73c66a6ccb8da092b117eb7d222
DOCKERFILES := apps/api/Dockerfile docker/renderer/Dockerfile
TRIVY_CACHE ?= $(HOME)/.cache/trivy
IMAGE ?= ohm-sweet-ohm-api

.PHONY: lint-docker scan-docker-config scan-docker-image build-api

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

scan-docker-image:
	mkdir -p "$(TRIVY_CACHE)"
	docker run --rm --user "$$(id -u):$$(id -g)" --group-add "$$(stat -c %g /var/run/docker.sock)" \
		-e TRIVY_CACHE_DIR=/cache -v "$(TRIVY_CACHE)":/cache \
		-v /var/run/docker.sock:/var/run/docker.sock \
		$(TRIVY_IMAGE) image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 $(IMAGE)
