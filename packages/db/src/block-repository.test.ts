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

function publishOne(input: BlockDraft) {
  const [block] = published(input);
  if (block === undefined) throw new Error('nothing published');
  return block;
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
    await sql`truncate blocks, block_specs`.execute(db);
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
    for (const block of [root, variant]) if (block !== undefined) await repository.save(block);

    const catalogue = await repository.loadCatalogue([ledResistor]);

    expect(snapshot(catalogue.findBlock('led-resistor-basic'))).toEqual(snapshot(root));
    expect(snapshot(catalogue.findBlock('led-two-in-series'))).toEqual(snapshot(variant));
  });

  it('rebuilds the variant tree with parents loaded before their variants', async () => {
    const blocks = published(
      draft(),
      draft({ slug: 'a', parentSlug: 'led-resistor-basic', changeSummary: 'two LEDs' }),
      draft({ slug: 'b', parentSlug: 'a', changeSummary: 'three LEDs' }),
    );
    for (const block of blocks) await repository.save(block);

    const catalogue = await repository.loadCatalogue([ledResistor]);

    expect(
      catalogue
        .findBlock('b')
        ?.path()
        .map((block) => block.slug),
    ).toEqual(['led-resistor-basic', 'a', 'b']);
  });

  it('replaces a block and its specs when saved again', async () => {
    await repository.save(publishOne(draft()));
    const second = publishOne(
      draft({
        name: 'Renamed',
        rawSpecs: LED_SPECS.filter((spec) => spec.key !== 'resistorPower'),
      }),
    );

    await repository.save(second);
    const loaded = (await repository.loadCatalogue([ledResistor])).findBlock('led-resistor-basic');

    expect([loaded?.name, loaded?.specFor('resistorPower')]).toEqual(['Renamed', undefined]);
  });

  it('refuses a stored block that breaks a domain rule', async () => {
    await repository.save(publishOne(draft()));
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

  it('refuses to save a variant before its parent', async () => {
    const [, variant] = published(
      draft(),
      draft({ slug: 'a', parentSlug: 'led-resistor-basic', changeSummary: 'x' }),
    );
    if (variant === undefined) throw new Error('nothing published');

    await expect(repository.save(variant)).rejects.toThrow(/foreign key/);
    expect(await db.selectFrom('blocks').select('slug').execute()).toEqual([]);
  });

  it('refuses stored blocks whose parents form a cycle', async () => {
    const blocks = published(
      draft(),
      draft({ slug: 'a', parentSlug: 'led-resistor-basic', changeSummary: 'x' }),
      draft({ slug: 'b', parentSlug: 'a', changeSummary: 'y' }),
    );
    for (const block of blocks) await repository.save(block);
    await db.updateTable('blocks').set({ parent_slug: 'b' }).where('slug', '=', 'a').execute();

    await expect(repository.loadCatalogue([ledResistor])).rejects.toThrow(
      'stored blocks with a missing or cyclic parent: a, b',
    );
  });

  it('refuses malformed key components stored outside the repository', async () => {
    await repository.save(publishOne(draft()));
    await db.updateTable('blocks').set({ key_components: '[{"partNumber": 1}]' }).execute();

    await expect(repository.loadCatalogue([ledResistor])).rejects.toThrow(
      'unexpected key_components in the database',
    );
  });

  it('enforces the variant summary rule in the schema itself', async () => {
    await repository.save(publishOne(draft()));

    await expect(
      db
        .updateTable('blocks')
        .set({ change_summary: 'not allowed on a root' })
        .where('slug', '=', 'led-resistor-basic')
        .execute(),
    ).rejects.toThrow(/blocks_variant_summary_check/);
  });
});
