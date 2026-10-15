import { PostgreSqlContainer, type StartedPostgreSqlContainer } from '@testcontainers/postgresql';
import type { FastifyInstance } from 'fastify';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';

import { BASE_CIRCUITS, type Block } from '@ohm-sweet-ohm/domain';
import { BlockRepository, createDatabase, migrateToLatest } from '@ohm-sweet-ohm/db';

import { buildApp } from './app.js';
import { CatalogueCache } from './catalogue-cache.js';
import { makeCatalogue } from './test-catalogue.js';

function blockOf(slug: string): Block {
  const block = makeCatalogue().findBlock(slug);
  if (block === undefined) throw new Error(`test catalogue has no ${slug}`);
  return block;
}

describe('API against PostgreSQL', () => {
  const clock = { now: 0 };
  let container: StartedPostgreSqlContainer;
  let db: ReturnType<typeof createDatabase>;
  let repository: BlockRepository;
  let app: FastifyInstance;

  beforeAll(async () => {
    container = await new PostgreSqlContainer('postgres:17-alpine').start();
    db = createDatabase(container.getConnectionUri(), (error) => {
      throw error;
    });
    await migrateToLatest(db);
    repository = new BlockRepository(db);
    await repository.mirror([{ block: blockOf('led-resistor-basic'), svg: '<svg>v1</svg>' }]);
    app = await buildApp({
      schematics: repository,
      catalogue: new CatalogueCache(
        {
          loadCatalogue: () => repository.loadCatalogue(BASE_CIRCUITS),
          catalogueVersion: () => repository.catalogueVersion(),
        },
        { checkIntervalMs: 5_000, now: () => clock.now, onCheckFailed: () => undefined },
      ),
    });
  }, 180_000);

  afterAll(async () => {
    await app.close();
    await db.destroy();
    await container.stop();
  });

  it('serves imported blocks and picks up a new import after the check interval', async () => {
    const before = await app.inject({ method: 'GET', url: '/blocks/led-pair' });

    await repository.mirror([
      { block: blockOf('led-resistor-basic'), svg: '<svg>v1</svg>' },
      { block: blockOf('led-pair'), svg: '<svg>pair</svg>' },
    ]);
    const withinInterval = await app.inject({ method: 'GET', url: '/blocks/led-pair' });
    clock.now = 5_000;
    const afterInterval = await app.inject({ method: 'GET', url: '/blocks/led-pair' });
    const svg = await app.inject({ method: 'GET', url: '/blocks/led-pair/schematic.svg' });

    expect([before.statusCode, withinInterval.statusCode, afterInterval.statusCode]).toEqual([
      404, 404, 200,
    ]);
    expect(afterInterval.json<{ path: { slug: string }[] }>().path.map(({ slug }) => slug)).toEqual(
      ['led-resistor-basic', 'led-pair'],
    );
    expect([svg.statusCode, svg.body]).toEqual([200, '<svg>pair</svg>']);
  });
});
