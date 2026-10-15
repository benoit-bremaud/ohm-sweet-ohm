import { BASE_CIRCUITS } from '@ohm-sweet-ohm/domain';
import { BlockRepository, createDatabase } from '@ohm-sweet-ohm/db';

import { buildApp } from './app.js';
import { CatalogueCache } from './catalogue-cache.js';

const databaseUrl = process.env.DATABASE_URL;
if (databaseUrl === undefined || databaseUrl === '') {
  console.error('DATABASE_URL is required');
  process.exit(2);
}

const db = createDatabase(databaseUrl, (error) => {
  app.log.warn({ err: error }, 'database connection lost; it reconnects on the next query');
});
const repository = new BlockRepository(db);
const app = await buildApp({
  logger: true,
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
        app.log.warn({ err: error }, 'catalogue check failed; serving the cached catalogue');
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
