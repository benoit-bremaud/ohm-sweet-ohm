import { BASE_CIRCUITS } from '@ohm-sweet-ohm/domain';
import { BlockRepository, createDatabase } from '@ohm-sweet-ohm/db';

import { pino } from 'pino';

import { buildApp } from './app.js';
import { CatalogueCache } from './catalogue-cache.js';
import { idleConnectionErrorHandler } from './logger.js';

const databaseUrl = process.env.DATABASE_URL;
if (databaseUrl === undefined || databaseUrl === '') {
  console.error('DATABASE_URL is required');
  process.exit(2);
}

// Created before the pool: its error callback may fire while buildApp is still running (#27).
const logger = pino();
const db = createDatabase(databaseUrl, idleConnectionErrorHandler(logger));
const repository = new BlockRepository(db);
const app = await buildApp({
  logger,
  schematics: repository,
  catalogue: new CatalogueCache(
    {
      loadCatalogue: () => repository.loadCatalogue(BASE_CIRCUITS),
      catalogueVersion: () => repository.catalogueVersion(),
    },
    {
      checkIntervalMs: 5_000,
      now: () => Date.now(),
      onCheckFailed: (error) => {
        logger.warn({ err: error }, 'catalogue check failed; serving the cached catalogue');
      },
    },
  ),
});

await app.listen({ host: process.env.HOST ?? '0.0.0.0', port: Number(process.env.PORT ?? 3000) });

// Docker and systemd stop with SIGTERM: finish in-flight requests, then close the pool.
for (const signal of ['SIGTERM', 'SIGINT'] as const) {
  process.once(signal, () => {
    void app.close().then(() => db.destroy());
  });
}
