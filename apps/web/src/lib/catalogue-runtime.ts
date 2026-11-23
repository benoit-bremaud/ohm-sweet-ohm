import { env } from 'cloudflare:workers';

import { BlockRepository, createDatabase } from '@ohm-sweet-ohm/db';
import { BASE_CIRCUITS } from '@ohm-sweet-ohm/domain';

import type { CatalogueReader } from './catalogue';
import { CatalogueCache } from './catalogue-cache';

/**
 * Wiring only (excluded from coverage, like the old API's main.ts): the catalogue database through
 * the Hyperdrive binding (ADR-0005). A Worker cannot reuse a connection across requests, so each
 * read opens one through Hyperdrive, which keeps the pool to Neon, and closes it.
 */
async function withRepository<T>(read: (repository: BlockRepository) => Promise<T>): Promise<T> {
  // The pool lives for one read: its only idle-connection error is the socket closing on destroy.
  // A failure during the read rejects the query and reaches the page.
  const db = createDatabase(env.HYPERDRIVE.connectionString, () => undefined);
  try {
    return await read(new BlockRepository(db));
  } finally {
    await db.destroy();
  }
}

// One cache per isolate: the catalogue is reloaded only after an import (PROJECT_LOG, 2026-10-14).
const cache = new CatalogueCache(
  {
    loadCatalogue: () => withRepository((r) => r.loadCatalogue(BASE_CIRCUITS)),
    catalogueVersion: () => withRepository((r) => r.catalogueVersion()),
  },
  {
    checkIntervalMs: 5_000,
    now: () => Date.now(),
    onCheckFailed: (error) => {
      console.warn('catalogue check failed; serving the cached catalogue', error);
    },
  },
);

/** The catalogue reader of the deployed Worker. */
export const catalogueReader: CatalogueReader = {
  catalogue: () => cache.get(),
  findSchematic: (slug) => withRepository((r) => r.findSchematic(slug)),
};
