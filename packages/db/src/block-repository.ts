import type { Kysely, Selectable } from 'kysely';

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
type SpecRow = Selectable<BlockSpecsTable>;
type MeasureQuantity = NonNullable<RawSpec['quantity']>;

/**
 * Persists published blocks and rebuilds the catalogue from them. Loading republishes every
 * stored block through `Catalogue.publish`, so the domain rules are checked again on read.
 */
export class BlockRepository {
  constructor(private readonly db: Kysely<Database>) {}

  /** Inserts or replaces a block and its specs in one transaction. Parents must be saved first. */
  async save(block: Block): Promise<void> {
    await this.db.transaction().execute(async (transaction) => {
      const row = {
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
      };
      await transaction
        .insertInto('blocks')
        .values(row)
        .onConflict((conflict) => conflict.column('slug').doUpdateSet(row))
        .execute();

      await transaction.deleteFrom('block_specs').where('block_slug', '=', block.slug).execute();
      const specs = block.specs.map((spec) => {
        const raw = spec.toRaw();
        return {
          block_slug: block.slug,
          key: raw.key,
          min: raw.min ?? null,
          max: raw.max ?? null,
          quantity: raw.quantity ?? null,
          text: raw.text ?? null,
        };
      });
      if (specs.length > 0) {
        await transaction.insertInto('block_specs').values(specs).execute();
      }
    });
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
