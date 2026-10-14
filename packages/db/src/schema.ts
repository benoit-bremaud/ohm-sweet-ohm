import type { ColumnType, Generated } from 'kysely';

/**
 * Row types of the tables created by the migrations in ./migrations. Kept by hand: the
 * integration tests round-trip every column through a real PostgreSQL, so a drift between this
 * file and a migration fails a test.
 */
export interface BlocksTable {
  slug: string;
  name: string;
  description: string;
  change_summary: string | null;
  base_circuit_slug: string;
  parent_slug: string | null;
  difficulty: string;
  validation_status: string;
  hazardous: boolean;
  /** jsonb: read as parsed JSON (checked by the repository), written as a JSON string. */
  key_components: ColumnType<unknown, string, string>;
  source_title: string;
  source_url: string | null;
  kicad_path: string;
  svg_path: string;
  published_at: Generated<Date>;
}

export interface BlockSpecsTable {
  block_slug: string;
  key: string;
  min: number | null;
  max: number | null;
  quantity: string | null;
  text: string | null;
}

export interface Database {
  blocks: BlocksTable;
  block_specs: BlockSpecsTable;
}
