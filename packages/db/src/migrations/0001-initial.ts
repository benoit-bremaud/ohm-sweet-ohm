import { type Kysely, sql } from 'kysely';

/** Blocks and their specs; base circuits are defined in code (packages/domain) and referenced by slug. */
export async function up(db: Kysely<unknown>): Promise<void> {
  await db.schema
    .createTable('blocks')
    .addColumn('slug', 'text', (column) => column.primaryKey())
    .addColumn('name', 'text', (column) => column.notNull())
    .addColumn('description', 'text', (column) => column.notNull())
    .addColumn('change_summary', 'text')
    .addColumn('base_circuit_slug', 'text', (column) => column.notNull())
    .addColumn('parent_slug', 'text', (column) => column.references('blocks.slug'))
    .addColumn('difficulty', 'text', (column) => column.notNull())
    .addColumn('validation_status', 'text', (column) => column.notNull())
    .addColumn('hazardous', 'boolean', (column) => column.notNull())
    .addColumn('key_components', 'jsonb', (column) => column.notNull().defaultTo(sql`'[]'::jsonb`))
    .addColumn('source_title', 'text', (column) => column.notNull())
    .addColumn('source_url', 'text')
    .addColumn('kicad_path', 'text', (column) => column.notNull())
    .addColumn('svg_path', 'text', (column) => column.notNull())
    .addColumn('published_at', 'timestamptz', (column) => column.notNull().defaultTo(sql`now()`))
    .addCheckConstraint(
      'blocks_difficulty_check',
      sql`difficulty in ('BEGINNER', 'INTERMEDIATE', 'ADVANCED')`,
    )
    .addCheckConstraint(
      'blocks_validation_status_check',
      sql`validation_status in ('TESTED', 'THEORETICAL')`,
    )
    .addCheckConstraint(
      'blocks_variant_summary_check',
      sql`(parent_slug is null) = (change_summary is null)`,
    )
    .execute();

  await db.schema
    .createTable('block_specs')
    .addColumn('block_slug', 'text', (column) =>
      column.notNull().references('blocks.slug').onDelete('cascade'),
    )
    .addColumn('key', 'text', (column) => column.notNull())
    .addColumn('min', 'double precision')
    .addColumn('max', 'double precision')
    .addColumn('quantity', 'text')
    .addColumn('text', 'text')
    .addPrimaryKeyConstraint('block_specs_pkey', ['block_slug', 'key'])
    .addCheckConstraint(
      'block_specs_range_check',
      sql`(min is null) = (max is null) and (min is null or min <= max)`,
    )
    .addCheckConstraint('block_specs_kind_check', sql`(text is null) <> (min is null)`)
    .addCheckConstraint(
      'block_specs_quantity_check',
      sql`quantity is null or (min is not null and quantity in ('VOLTAGE', 'CURRENT', 'RESISTANCE', 'FREQUENCY', 'POWER'))`,
    )
    .execute();
}

/** Drops the initial schema, children first. */
export async function down(db: Kysely<unknown>): Promise<void> {
  await db.schema.dropTable('block_specs').execute();
  await db.schema.dropTable('blocks').execute();
}
