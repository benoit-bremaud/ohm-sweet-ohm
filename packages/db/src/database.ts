import { Kysely, PostgresDialect } from 'kysely';
import { type Migration, type MigrationResultSet, Migrator } from 'kysely/migration';
import pg from 'pg';

import * as initial from './migrations/0001-initial.js';
import * as schematicsAndContentHash from './migrations/0002-schematics-and-content-hash.js';
import type { Database } from './schema.js';

/** Migrations in apply order; new ones are appended, never edited once merged. */
const MIGRATIONS: Readonly<Record<string, Migration>> = {
  '0001-initial': initial,
  '0002-schematics-and-content-hash': schematicsAndContentHash,
};

/**
 * When the server drops an idle connection (restart, outage), the pool emits an error that would
 * crash the process if nobody listened: it is reported instead, and the next query reconnects.
 */
export function createDatabase(
  connectionString: string,
  onIdleConnectionError: (error: Error) => void,
): Kysely<Database> {
  const pool = new pg.Pool({ connectionString });
  pool.on('error', onIdleConnectionError);
  return new Kysely<Database>({ dialect: new PostgresDialect({ pool }) });
}

/** Applies every pending migration; throws with the failing migration's error. */
export async function migrateToLatest(db: Kysely<Database>): Promise<MigrationResultSet> {
  const migrator = new Migrator({
    db,
    provider: { getMigrations: () => Promise.resolve(MIGRATIONS) },
  });
  const result = await migrator.migrateToLatest();
  if (result.error !== undefined) {
    throw result.error instanceof Error
      ? result.error
      : new Error('migration failed', { cause: result.error });
  }
  return result;
}
