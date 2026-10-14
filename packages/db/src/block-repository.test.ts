import { PostgreSqlContainer, type StartedPostgreSqlContainer } from '@testcontainers/postgresql';
import { type Kysely, sql } from 'kysely';
import { afterAll, beforeAll, beforeEach, describe, expect, it } from 'vitest';

import {
  type Block,
  type BlockDraft,
  Catalogue,
  ledResistor,
  type RawSpec,
} from '@ohm-sweet-ohm/domain';

import { BlockRepository } from './block-repository.js';
import { createDatabase, migrateToLatest } from './database.js';
import type { Database } from './schema.js';

const LED_SPECS: readonly RawSpec[] = [
  { key: 'supplyVoltage', min: 5, max: 5, quantity: 'VOLTAGE' },
  { key: 'ledCurrent', min: 0.0136, max: 0.0136, quantity: 'CURRENT' },
  { key: 'ledColor', text: 'red' },
  { key: 'ledCount', min: 1, max: 1 },
  { key: 'resistorPower', min: 0.041, max: 0.041, quantity: 'POWER' },
];

function draft(overrides: Partial<BlockDraft> = {}): BlockDraft {
  return {
    slug: 'led-resistor-basic',
    name: 'LED with current-limiting resistor',
    description: 'A red LED on 5 V through 220 Ω.',
    baseCircuitSlug: 'led-resistor',
    difficulty: 'BEGINNER',
    validationStatus: 'THEORETICAL',
    hazardous: false,
    rawSpecs: LED_SPECS,
    keyComponents: [{ partNumber: 'L-53HD', role: 'Red 5 mm LED' }],
    source: { title: 'Ohm Sweet Ohm original design', url: 'https://example.com/led' },
    schematic: {
      kicadPath: 'led-resistor/led-resistor-basic/schematic.kicad_sch',
      svgPath: 'led-resistor/led-resistor-basic/schematic.svg',
    },
    ...overrides,
  };
}

/** Publishes drafts in a fresh catalogue and returns the published blocks, in order. */
function published(...drafts: BlockDraft[]) {
  const catalogue = new Catalogue([ledResistor]);
  return drafts.map((input) => {
    expect(catalogue.publish(input)).toEqual([]);
    const block = catalogue.findBlock(input.slug);
    if (block === undefined) throw new Error(`not published: ${input.slug}`);
    return block;
  });
}

/** Every persisted field of a block as plain data, so a round trip compares all columns. */
function snapshot(block: Block | undefined) {
  if (block === undefined) return undefined;
  return {
    slug: block.slug,
    name: block.name,
    description: block.description,
    changeSummary: block.changeSummary,
    baseCircuit: block.baseCircuit.slug,
    parent: block.parent?.slug,
    difficulty: block.difficulty,
    validationStatus: block.validationStatus,
    hazardous: block.hazardous,
    specs: block.specs.map((spec) => spec.toRaw()).sort((a, b) => a.key.localeCompare(b.key)),
    keyComponents: block.keyComponents,
    source: block.source,
    schematic: block.schematic,
  };
}

/** Mirrors the given blocks, each with a recognisable placeholder schematic. */
function entries(blocks: readonly Block[]) {
  return blocks.map((block) => ({ block, svg: `<svg>${block.slug}</svg>` }));
}

const VARIANT_A = draft({ slug: 'a', parentSlug: 'led-resistor-basic', changeSummary: 'two LEDs' });
const VARIANT_B = draft({ slug: 'b', parentSlug: 'a', changeSummary: 'three LEDs' });

describe('BlockRepository', () => {
  let container: StartedPostgreSqlContainer;
  let db: Kysely<Database>;
  let repository: BlockRepository;

  beforeAll(async () => {
    container = await new PostgreSqlContainer('postgres:17-alpine').start();
    db = createDatabase(container.getConnectionUri());
    await migrateToLatest(db);
    repository = new BlockRepository(db);
  }, 180_000);

  afterAll(async () => {
    await db.destroy();
    await container.stop();
  });

  beforeEach(async () => {
    await sql`truncate blocks, block_specs, block_schematics`.execute(db);
  });

  it('applies migrations only once', async () => {
    const second = await migrateToLatest(db);

    expect(second.results).toEqual([]);
  });

  it('round-trips every field of a root block and of a variant without source URL', async () => {
    const [root, variant] = published(
      draft(),
      draft({
        slug: 'led-two-in-series',
        parentSlug: 'led-resistor-basic',
        changeSummary: 'Two LEDs in series',
        validationStatus: 'TESTED',
        difficulty: 'INTERMEDIATE',
        hazardous: true,
        keyComponents: [],
        source: { title: 'Bench notes' },
      }),
    );
    if (root === undefined || variant === undefined) throw new Error('nothing published');

    await repository.mirror(entries([root, variant]));
    const catalogue = await repository.loadCatalogue([ledResistor]);

    expect(snapshot(catalogue.findBlock('led-resistor-basic'))).toEqual(snapshot(root));
    expect(snapshot(catalogue.findBlock('led-two-in-series'))).toEqual(snapshot(variant));
  });

  it('writes parents first even when variants are given first', async () => {
    const blocks = published(draft(), VARIANT_A, VARIANT_B);

    await repository.mirror(entries([...blocks].reverse()));
    const catalogue = await repository.loadCatalogue([ledResistor]);

    expect(
      catalogue
        .findBlock('b')
        ?.path()
        .map((block) => block.slug),
    ).toEqual(['led-resistor-basic', 'a', 'b']);
  });

  it('stores each schematic with its block', async () => {
    await repository.mirror(entries(published(draft(), VARIANT_A)));

    const rows = await db
      .selectFrom('block_schematics')
      .selectAll()
      .orderBy('block_slug')
      .execute();

    expect(rows).toEqual([
      { block_slug: 'a', svg: '<svg>a</svg>' },
      { block_slug: 'led-resistor-basic', svg: '<svg>led-resistor-basic</svg>' },
    ]);
  });

  it('reports added, then unchanged blocks, and rewrites nothing the second time', async () => {
    const first = await repository.mirror(entries(published(draft(), VARIANT_A)));
    const [before] = await db
      .selectFrom('blocks')
      .select('updated_at')
      .where('slug', '=', 'a')
      .execute();

    const second = await repository.mirror(entries(published(draft(), VARIANT_A)));
    const [after] = await db
      .selectFrom('blocks')
      .select('updated_at')
      .where('slug', '=', 'a')
      .execute();

    expect(first).toEqual({
      added: ['led-resistor-basic', 'a'],
      changed: [],
      unchanged: [],
      removed: [],
    });
    expect(second).toEqual({
      added: [],
      changed: [],
      unchanged: ['led-resistor-basic', 'a'],
      removed: [],
    });
    expect(after?.updated_at).toEqual(before?.updated_at);
  });

  it('rewrites a changed block and its specs, keeping its first publication date', async () => {
    await repository.mirror(entries(published(draft())));
    const [before] = await db.selectFrom('blocks').select('published_at').execute();

    const summary = await repository.mirror(
      entries(
        published(
          draft({
            name: 'Renamed',
            rawSpecs: LED_SPECS.filter((spec) => spec.key !== 'resistorPower'),
          }),
        ),
      ),
    );
    const loaded = (await repository.loadCatalogue([ledResistor])).findBlock('led-resistor-basic');
    const [after] = await db.selectFrom('blocks').select('published_at').execute();

    expect(summary.changed).toEqual(['led-resistor-basic']);
    expect([loaded?.name, loaded?.specFor('resistorPower')]).toEqual(['Renamed', undefined]);
    expect(after?.published_at).toEqual(before?.published_at);
  });

  it('treats a changed schematic alone as a change', async () => {
    const [block] = published(draft());
    if (block === undefined) throw new Error('nothing published');
    await repository.mirror([{ block, svg: '<svg>v1</svg>' }]);

    const summary = await repository.mirror([{ block, svg: '<svg>v2</svg>' }]);

    expect(summary.changed).toEqual(['led-resistor-basic']);
  });

  it('removes blocks no longer given, with their specs and schematics', async () => {
    await repository.mirror(entries(published(draft(), VARIANT_A, VARIANT_B)));

    const summary = await repository.mirror(entries(published(draft())));

    expect(summary.removed).toEqual(['a', 'b']);
    expect(await db.selectFrom('block_specs').select('block_slug').distinct().execute()).toEqual([
      { block_slug: 'led-resistor-basic' },
    ]);
    expect(await db.selectFrom('block_schematics').select('block_slug').execute()).toEqual([
      { block_slug: 'led-resistor-basic' },
    ]);
  });

  it('moves a block to a new parent while its former parent is removed', async () => {
    await repository.mirror(entries(published(draft(), VARIANT_A, VARIANT_B)));
    const moved = draft({
      slug: 'b',
      parentSlug: 'led-resistor-basic',
      changeSummary: 'three LEDs',
    });

    const summary = await repository.mirror(entries(published(draft(), moved)));
    const catalogue = await repository.loadCatalogue([ledResistor]);

    expect(summary).toEqual({
      added: [],
      changed: ['b'],
      unchanged: ['led-resistor-basic'],
      removed: ['a'],
    });
    expect(
      catalogue
        .findBlock('b')
        ?.path()
        .map((block) => block.slug),
    ).toEqual(['led-resistor-basic', 'b']);
  });

  it('rewrites a changed parent without touching its unchanged variants', async () => {
    await repository.mirror(entries(published(draft(), VARIANT_A)));
    const [before] = await db
      .selectFrom('blocks')
      .select('updated_at')
      .where('slug', '=', 'a')
      .execute();

    const summary = await repository.mirror(
      entries(published(draft({ name: 'Renamed root' }), VARIANT_A)),
    );
    const [after] = await db
      .selectFrom('blocks')
      .select('updated_at')
      .where('slug', '=', 'a')
      .execute();

    expect(summary).toEqual({
      added: [],
      changed: ['led-resistor-basic'],
      unchanged: ['a'],
      removed: [],
    });
    expect(after?.updated_at).toEqual(before?.updated_at);
  });

  it('gives the same content hash whatever the order of the specs', async () => {
    await repository.mirror(entries(published(draft())));

    const summary = await repository.mirror(
      entries(published(draft({ rawSpecs: [...LED_SPECS].reverse() }))),
    );

    expect(summary.unchanged).toEqual(['led-resistor-basic']);
  });

  it('leaves the database unchanged when a mirror fails', async () => {
    await repository.mirror(entries(published(draft(), VARIANT_A)));
    const orphan = published(
      draft(),
      VARIANT_A,
      draft({ slug: 'orphan', parentSlug: 'a', changeSummary: 'x' }),
    ).find((block) => block.slug === 'orphan');
    if (orphan === undefined) throw new Error('nothing published');

    // Given alone, the orphan's parent "a" would be removed, breaking the foreign key mid-mirror.
    await expect(repository.mirror(entries([orphan]))).rejects.toThrow(/foreign key/);
    const slugs = await db.selectFrom('blocks').select('slug').orderBy('slug').execute();
    expect(slugs.map((row) => row.slug)).toEqual(['a', 'led-resistor-basic']);
  });

  it('refuses a stored block that breaks a domain rule', async () => {
    await repository.mirror(entries(published(draft())));
    await db
      .insertInto('block_specs')
      .values({
        block_slug: 'led-resistor-basic',
        key: 'typo',
        min: null,
        max: null,
        quantity: null,
        text: 'x',
      })
      .execute();

    await expect(repository.loadCatalogue([ledResistor])).rejects.toThrow(
      'stored block led-resistor-basic breaks the catalogue rules: specs.typo: unknown parameter for led-resistor',
    );
  });

  it('refuses stored blocks whose parents form a cycle', async () => {
    await repository.mirror(entries(published(draft(), VARIANT_A, VARIANT_B)));
    await db.updateTable('blocks').set({ parent_slug: 'b' }).where('slug', '=', 'a').execute();

    await expect(repository.loadCatalogue([ledResistor])).rejects.toThrow(
      'stored blocks with a missing or cyclic parent: a, b',
    );
  });

  it('refuses malformed key components stored outside the repository', async () => {
    await repository.mirror(entries(published(draft())));
    await db.updateTable('blocks').set({ key_components: '[{"partNumber": 1}]' }).execute();

    await expect(repository.loadCatalogue([ledResistor])).rejects.toThrow(
      'unexpected key_components in the database',
    );
  });

  it('enforces the variant summary rule in the schema itself', async () => {
    await repository.mirror(entries(published(draft())));

    await expect(
      db
        .updateTable('blocks')
        .set({ change_summary: 'not allowed on a root' })
        .where('slug', '=', 'led-resistor-basic')
        .execute(),
    ).rejects.toThrow(/blocks_variant_summary_check/);
  });
});
