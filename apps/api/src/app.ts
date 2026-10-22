import fastifySwagger from '@fastify/swagger';
import fastifySwaggerUi from '@fastify/swagger-ui';
import Fastify, { type FastifyBaseLogger, type FastifyError, type FastifyInstance } from 'fastify';
import {
  jsonSchemaTransform,
  serializerCompiler,
  validatorCompiler,
  type ZodTypeProvider,
} from 'fastify-type-provider-zod';
import * as z from 'zod';

import { blockResponseSchema, errorResponseSchema, SLUG_PATTERN } from '@ohm-sweet-ohm/schemas';

import type { CatalogueCache } from './catalogue-cache.js';
import { toBlockResponse } from './to-block-response.js';

/** Where the API reads rendered schematics; resolves to undefined for an unknown slug. */
export interface SchematicSource {
  findSchematic(
    slug: string,
  ): Promise<{ readonly svg: string; readonly contentHash: string } | undefined>;
}

/** What buildApp needs from the outside, injected so tests run without a database. */
export interface AppDependencies {
  readonly catalogue: Pick<CatalogueCache, 'get'>;
  readonly schematics: SchematicSource;
  /** Shared with code that logs before the app exists (the pool); omitted, the app stays silent. */
  readonly logger?: FastifyBaseLogger;
}

const slugParams = z.object({ slug: z.string().regex(SLUG_PATTERN) });

/**
 * SVGs are served as images that can never run code, even if a future contributed schematic
 * carried a script: no script, no plugin, sandboxed, and no MIME sniffing.
 */
const SVG_HEADERS = {
  'content-type': 'image/svg+xml; charset=utf-8',
  'content-security-policy': "default-src 'none'; style-src 'unsafe-inline'; sandbox",
  'x-content-type-options': 'nosniff',
  // Kept by caches but revalidated every time (a cheap 304), so an import shows at once.
  'cache-control': 'public, no-cache',
} as const;

/** Builds the Fastify app: block and schematic routes, OpenAPI docs and the `{ error }` error shape. */
export async function buildApp({
  catalogue,
  schematics,
  logger,
}: AppDependencies): Promise<FastifyInstance> {
  const app = Fastify(logger === undefined ? { logger: false } : { loggerInstance: logger });
  app.setValidatorCompiler(validatorCompiler);
  app.setSerializerCompiler(serializerCompiler);
  // Every error uses the documented { error } shape; server failures never expose internals.
  app.setErrorHandler((error: FastifyError, request, reply) => {
    const status = error.statusCode ?? 500;
    if (status >= 500) {
      request.log.error({ err: error }, 'request failed');
      return reply.code(500).send({ error: 'internal server error' });
    }
    return reply.code(status).send({ error: error.message });
  });
  app.setNotFoundHandler((request, reply) =>
    reply.code(404).send({ error: `no route ${request.method} ${request.url}` }),
  );

  await app.register(fastifySwagger, {
    openapi: {
      info: {
        title: 'Ohm Sweet Ohm API',
        description: 'Reusable electronic circuit blocks and their variants.',
        version: '0.1.0',
      },
    },
    transform: jsonSchemaTransform,
  });
  await app.register(fastifySwaggerUi, { routePrefix: '/docs' });

  const routes = app.withTypeProvider<ZodTypeProvider>();

  routes.get('/health', { schema: { hide: true } }, () => ({ status: 'ok' }));

  routes.get(
    '/blocks/:slug',
    {
      schema: {
        summary: 'Get a block',
        params: slugParams,
        response: { 200: blockResponseSchema, 404: errorResponseSchema },
      },
    },
    async (request, reply) => {
      const block = (await catalogue.get()).findBlock(request.params.slug);
      if (block === undefined) {
        return reply.code(404).send({ error: `no block "${request.params.slug}"` });
      }
      return toBlockResponse(block);
    },
  );

  routes.get(
    '/blocks/:slug/schematic.svg',
    {
      schema: {
        summary: "Get a block's rendered schematic (SVG)",
        params: slugParams,
        response: {
          200: {
            description: 'Cropped SVG schematic',
            content: { 'image/svg+xml': { schema: z.string() } },
          },
          304: { description: 'Not modified', content: { 'text/plain': { schema: z.string() } } },
          404: errorResponseSchema,
        },
      },
    },
    async (request, reply) => {
      const schematic = await schematics.findSchematic(request.params.slug);
      if (schematic === undefined) {
        return reply.code(404).send({ error: `no schematic for "${request.params.slug}"` });
      }
      const etag = `"${schematic.contentHash}"`;
      void reply.headers({ ...SVG_HEADERS, etag });
      if (matchesEtag(request.headers['if-none-match'], etag)) {
        return reply.code(304).send('');
      }
      return reply.code(200).send(schematic.svg);
    },
  );

  return app;
}

/** RFC 9110 weak comparison: a list of tags, possibly weak (proxies add W/), or "*". */
function matchesEtag(ifNoneMatch: string | undefined, etag: string): boolean {
  return (
    ifNoneMatch?.split(',').some((tag) => {
      const candidate = tag.trim();
      return candidate === '*' || candidate.replace(/^W\//, '') === etag;
    }) ?? false
  );
}
