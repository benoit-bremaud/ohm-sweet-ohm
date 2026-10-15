# syntax=docker/dockerfile:1
# Catalogue API image (ADR-0004). Build context is the repository root:
#   docker build -f apps/api/Dockerfile -t ohm-sweet-ohm-api .
# Stage 1 bundles the API with its workspace packages (apps/api/build.ts) and prunes the npm
# packages to the API's production set; stage 2 keeps only Node, the bundle and those packages,
# and runs as the unprivileged `node` user. Alpine rather than Debian slim: no perl, fewer
# packages to carry vulnerabilities, and the API has no native dependency.

FROM node:22.23.3-alpine3.23@sha256:baf676f7d0e552f3231945c2f979055ca121bce128c152f7a34e6bd1728b1c5a AS build

WORKDIR /app
# pnpm version from package.json#packageManager, through the corepack shipped with Node 22.
RUN corepack enable

# Manifests first so the dependency layer is cached until a manifest changes.
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml tsconfig.base.json ./
COPY apps/api/package.json apps/api/
COPY apps/importer/package.json apps/importer/
COPY apps/web/package.json apps/web/
COPY packages/db/package.json packages/db/
COPY packages/domain/package.json packages/domain/
COPY packages/schemas/package.json packages/schemas/
RUN pnpm install --frozen-lockfile --filter @ohm-sweet-ohm/api...

COPY apps/api apps/api
COPY packages packages
RUN pnpm --filter @ohm-sweet-ohm/api build

# Production npm packages of the API and of the bundled workspace packages, hoisted into one flat
# node_modules so the bundle resolves them. `--legacy`: pnpm 10's default deploy needs injected
# workspace packages, which the workspace does not use. The workspace packages themselves are
# already inside the bundle.
RUN pnpm --filter @ohm-sweet-ohm/api --prod deploy --legacy --config.node-linker=hoisted /prod \
  && rm -rf /prod/node_modules/@ohm-sweet-ohm

FROM node:22.23.3-alpine3.23@sha256:baf676f7d0e552f3231945c2f979055ca121bce128c152f7a34e6bd1728b1c5a AS runtime

ENV NODE_ENV=production
ENV PORT=3000
WORKDIR /app

# The image only runs `node dist/main.js`: npm, npx, corepack and yarn are removed with their
# bundled dependencies, which otherwise show up in vulnerability scans.
RUN rm -rf /usr/local/lib/node_modules /usr/local/bin/npm /usr/local/bin/npx \
  /usr/local/bin/corepack /usr/local/bin/yarn /usr/local/bin/yarnpkg /opt/yarn-*

# package.json carries "type": "module", which Node needs to load dist/main.js as ESM.
COPY --from=build /app/apps/api/package.json ./
COPY --from=build /prod/node_modules ./node_modules
COPY --from=build /app/apps/api/dist ./dist

# `node` is UID 1000 in the official image; nothing is mounted, so no ownership fix is needed.
USER 1000
EXPOSE 3000

# Liveness only: /health answers as soon as the process is up, whatever the database does.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD ["node", "-e", "fetch(`http://127.0.0.1:${process.env.PORT}/health`).then((r) => process.exit(r.ok ? 0 : 1), () => process.exit(1))"]

CMD ["node", "dist/main.js"]
