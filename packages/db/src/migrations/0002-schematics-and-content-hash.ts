import { type Kysely, sql } from 'kysely';

/**
 * Rendered schematics in their own table, so the catalogue loaded in memory never carries them,
 * and a content hash per block so the importer's mirror rewrites changed blocks only. Rows stored
 * before this migration get an empty hash, so the first import afterwards reports them as changed.
 */
export async function up(db: Kysely<unknown>): Promise<void> {
  await db.schema
    .createTable('block_schematics')
    .addColumn('block_slug', 'text', (column) =>
      column.primaryKey().references('blocks.slug').onDelete('cascade'),
    )
    .addColumn('svg', 'text', (column) => column.notNull())
    .execute();

  await db.schema
    .alterTable('blocks')
    .addColumn('content_hash', 'text', (column) => column.notNull().defaultTo(''))
    .addColumn('updated_at', 'timestamptz', (column) => column.notNull().defaultTo(sql`now()`))
    .execute();
}

/** Reverts migration 0002. */
export async function down(db: Kysely<unknown>): Promise<void> {
  await db.schema
    .alterTable('blocks')
    .dropColumn('updated_at')
    .dropColumn('content_hash')
    .execute();
  await db.schema.dropTable('block_schematics').execute();
}
