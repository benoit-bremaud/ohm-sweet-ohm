import { createHash } from 'node:crypto';

import { type Kysely, type Selectable, sql } from 'kysely';

import {
  type BaseCircuit,
  type Block,
  type BlockDraft,
  type KeyComponent,
  Catalogue,
  DIFFICULTIES,
  type Difficulty,
  QUANTITIES,
  type RawSpec,
  VALIDATION_STATUSES,
  type ValidationStatus,
} from '@ohm-sweet-ohm/domain';

import type { BlockSpecsTable, BlocksTable, Database } from './schema.js';

type BlockRow = Selectable<BlocksTable>;

/** Advisory lock key serialising mirrors; any constant unique to this application. */
const MIRROR_LOCK = 7_013_331;

/** A published block with its rendered, cropped schematic. */
export interface SchematicBlock {
  readonly block: Block;
  readonly svg: string;
}

/** What a mirror changed, by block slug. */
export interface MirrorSummary {
  readonly added: readonly string[];
  readonly changed: readonly string[];
  readonly unchanged: readonly string[];
  readonly removed: readonly string[];
}
type SpecRow = Selectable<BlockSpecsTable>;
type MeasureQuantity = NonNullable<RawSpec['quantity']>;

/**
 * Persists published blocks and rebuilds the catalogue from them. Loading republishes every
 * stored block through `Catalogue.publish`, so the domain rules are checked again on read.
 */
export class BlockRepository {
  constructor(private readonly db: Kysely<Database>) {}

  /**
   * Makes the database an exact mirror of the given blocks, in one transaction: inserts added
   * blocks, rewrites changed ones (by content hash, so unchanged blocks keep their dates) and
   * deletes the blocks that are no longer given. Readers see either the old or the new catalogue.
   */
  async mirror(entries: readonly SchematicBlock[]): Promise<MirrorSummary> {
    const ordered = [...entries].sort((a, b) => a.block.path().length - b.block.path().length);
    return this.db.transaction().execute(async (transaction) => {
      // Concurrent mirrors (two CI jobs) queue here; readers are never blocked.
      await sql`select pg_advisory_xact_lock(${MIRROR_LOCK})`.execute(transaction);
      const stored = await transaction
        .selectFrom('blocks')
        .select(['slug', 'content_hash'])
        .execute();
      const storedHashes = new Map(stored.map((row) => [row.slug, row.content_hash]));
      const summary: {
        added: string[];
        changed: string[];
        unchanged: string[];
        removed: string[];
      } = {
        added: [],
        changed: [],
        unchanged: [],
        removed: [],
      };

      // Parents first, so a new variant's parent row exists before the variant references it.
      for (const entry of ordered) {
        const { block } = entry;
        const row = toRow(block, contentHash(entry));
        const storedHash = storedHashes.get(block.slug);
        if (storedHash === row.content_hash) {
          summary.unchanged.push(block.slug);
          continue;
        }
        (storedHash === undefined ? summary.added : summary.changed).push(block.slug);
        await transaction
          .insertInto('blocks')
          .values(row)
          .onConflict((conflict) =>
            conflict.column('slug').doUpdateSet({ ...row, updated_at: sql`now()` }),
          )
          .execute();
        await transaction.deleteFrom('block_specs').where('block_slug', '=', block.slug).execute();
        const specs = block.specs.map((spec) => toSpecRow(block.slug, spec.toRaw()));
        if (specs.length > 0) {
          await transaction.insertInto('block_specs').values(specs).execute();
        }
        await transaction
          .insertInto('block_schematics')
          .values({ block_slug: block.slug, svg: entry.svg })
          .onConflict((conflict) => conflict.column('block_slug').doUpdateSet({ svg: entry.svg }))
          .execute();
      }

      // Deleted last: once every kept block points to its new parent, no kept row references them.
      const kept = new Set(entries.map((entry) => entry.block.slug));
      summary.removed = [...storedHashes.keys()].filter((slug) => !kept.has(slug)).sort();
      if (summary.removed.length > 0) {
        await transaction.deleteFrom('blocks').where('slug', 'in', summary.removed).execute();
      }
      return summary;
    });
  }

  /**
   * A fingerprint of the whole stored catalogue: it changes whenever a mirror adds, changes or
   * removes a block, and costs one cheap query, so readers can reload only when needed.
   */
  async catalogueVersion(): Promise<string> {
    const { rows } = await sql<{ version: string | null }>`
      select md5(string_agg(slug || ':' || content_hash, ',' order by slug)) as version from blocks
    `.execute(this.db);
    return rows[0]?.version ?? 'empty';
  }

  /** The rendered schematic of a block, with the block's content hash for HTTP caching. */
  async findSchematic(
    slug: string,
  ): Promise<{ readonly svg: string; readonly contentHash: string } | undefined> {
    const row = await this.db
      .selectFrom('block_schematics')
      .innerJoin('blocks', 'blocks.slug', 'block_schematics.block_slug')
      .select(['block_schematics.svg', 'blocks.content_hash'])
      .where('block_schematics.block_slug', '=', slug)
      .executeTakeFirst();
    return row === undefined ? undefined : { svg: row.svg, contentHash: row.content_hash };
  }

  /**
   * Rebuilds a catalogue holding every stored block. Throws if a stored block breaks a domain
   * rule, which means the database was changed outside this repository.
   */
  async loadCatalogue(baseCircuits: readonly BaseCircuit[]): Promise<Catalogue> {
    // One snapshot for both tables, so a concurrent save never mixes old and new rows.
    const { blocks, specs } = await this.db
      .transaction()
      .setIsolationLevel('repeatable read')
      .execute(async (transaction) => ({
        blocks: await transaction.selectFrom('blocks').selectAll().execute(),
        specs: await transaction.selectFrom('block_specs').selectAll().execute(),
      }));
    const specsBySlug = Map.groupBy(specs, (spec) => spec.block_slug);
    const catalogue = new Catalogue(baseCircuits);
    for (const row of parentsFirst(blocks)) {
      const draft = toDraft(row, specsBySlug.get(row.slug) ?? []);
      const errors = catalogue.publish(draft);
      if (errors.length > 0) {
        const details = errors.map((error) => `${error.field}: ${error.message}`).join('; ');
        throw new Error(`stored block ${row.slug} breaks the catalogue rules: ${details}`);
      }
    }
    return catalogue;
  }
}

function toRow(block: Block, content_hash: string) {
  return {
    slug: block.slug,
    name: block.name,
    description: block.description,
    change_summary: block.changeSummary ?? null,
    base_circuit_slug: block.baseCircuit.slug,
    parent_slug: block.parent?.slug ?? null,
    difficulty: block.difficulty,
    validation_status: block.validationStatus,
    hazardous: block.hazardous,
    key_components: JSON.stringify(block.keyComponents),
    source_title: block.source.title,
    source_url: block.source.url ?? null,
    kicad_path: block.schematic.kicadPath,
    svg_path: block.schematic.svgPath,
    content_hash,
  };
}

function toSpecRow(blockSlug: string, raw: RawSpec) {
  return {
    block_slug: blockSlug,
    key: raw.key,
    min: raw.min ?? null,
    max: raw.max ?? null,
    quantity: raw.quantity ?? null,
    text: raw.text ?? null,
  };
}

/**
 * Hash of everything stored for a block. Specs are sorted by code point, not locale, so the hash
 * is the same on every machine. The key order of `toRow` and `toRaw` objects is part of the hash:
 * reordering their keys marks every block as changed once.
 */
function contentHash({ block, svg }: SchematicBlock): string {
  const content = {
    ...toRow(block, ''),
    specs: block.specs
      .map((spec) => spec.toRaw())
      .sort((a, b) => (a.key < b.key ? -1 : a.key > b.key ? 1 : 0)),
    svg,
  };
  return createHash('sha256').update(JSON.stringify(content)).digest('hex');
}

/** Orders rows so that every parent comes before its variants. */
function parentsFirst(rows: readonly BlockRow[]): readonly BlockRow[] {
  const ordered: BlockRow[] = [];
  const placed = new Set<string>();
  let pending = [...rows];
  while (pending.length > 0) {
    const ready = pending.filter((row) => row.parent_slug === null || placed.has(row.parent_slug));
    if (ready.length === 0) {
      throw new Error(
        `stored blocks with a missing or cyclic parent: ${pending
          .map((row) => row.slug)
          .sort()
          .join(', ')}`,
      );
    }
    for (const row of ready) {
      ordered.push(row);
      placed.add(row.slug);
    }
    pending = pending.filter((row) => !placed.has(row.slug));
  }
  return ordered;
}

function toDraft(row: BlockRow, specs: readonly SpecRow[]): BlockDraft {
  return {
    slug: row.slug,
    name: row.name,
    description: row.description,
    ...(row.change_summary === null ? {} : { changeSummary: row.change_summary }),
    baseCircuitSlug: row.base_circuit_slug,
    ...(row.parent_slug === null ? {} : { parentSlug: row.parent_slug }),
    difficulty: oneOf<Difficulty>(DIFFICULTIES, row.difficulty, 'difficulty'),
    validationStatus: oneOf<ValidationStatus>(
      VALIDATION_STATUSES,
      row.validation_status,
      'validation_status',
    ),
    hazardous: row.hazardous,
    rawSpecs: specs.map(toRawSpec),
    keyComponents: toKeyComponents(row.key_components),
    source: {
      title: row.source_title,
      ...(row.source_url === null ? {} : { url: row.source_url }),
    },
    schematic: { kicadPath: row.kicad_path, svgPath: row.svg_path },
  };
}

function toRawSpec(row: SpecRow): RawSpec {
  return {
    key: row.key,
    ...(row.min === null ? {} : { min: row.min }),
    ...(row.max === null ? {} : { max: row.max }),
    ...(row.quantity === null
      ? {}
      : {
          quantity: oneOf<MeasureQuantity>(
            QUANTITIES.filter((quantity) => quantity !== 'COUNT'),
            row.quantity,
            'quantity',
          ),
        }),
    ...(row.text === null ? {} : { text: row.text }),
  };
}

/** Checks the jsonb column, which the schema cannot constrain, before it reaches the domain. */
function toKeyComponents(value: unknown): readonly KeyComponent[] {
  const isKeyComponent = (item: unknown): item is KeyComponent =>
    typeof item === 'object' &&
    item !== null &&
    'partNumber' in item &&
    typeof item.partNumber === 'string' &&
    'role' in item &&
    typeof item.role === 'string';
  if (!Array.isArray(value) || !value.every(isKeyComponent)) {
    throw new Error('unexpected key_components in the database');
  }
  return value.map(({ partNumber, role }) => ({ partNumber, role }));
}

function oneOf<T extends string>(allowed: readonly T[], value: string, column: string): T {
  const match = allowed.find((candidate) => candidate === value);
  if (match === undefined) {
    throw new Error(`unexpected ${column} "${value}" in the database`);
  }
  return match;
}
