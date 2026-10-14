import { cp, mkdir, mkdtemp, readFile, rm, symlink, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

import { afterEach, beforeEach, describe, expect, it } from 'vitest';

import type { MirrorSummary, SchematicBlock } from '@ohm-sweet-ohm/db';

import { importCatalogue } from './import-catalogue.js';

const REAL_CATALOGUE = new URL('../../../catalogue', import.meta.url).pathname;
const LED = 'led-resistor/led-resistor-basic';

/** Records what would be mirrored; the database itself is covered by import.int.test.ts. */
class RecordingRepository {
  mirrored: readonly SchematicBlock[] | undefined;

  mirror(entries: readonly SchematicBlock[]): Promise<MirrorSummary> {
    this.mirrored = entries;
    return Promise.resolve({
      added: entries.map((entry) => entry.block.slug),
      changed: [],
      unchanged: [],
      removed: [],
    });
  }
}

let root: string;
let catalogueDir: string;
let renderDir: string;
let repository: RecordingRepository;

async function addVariant(slug: string, parent: string): Promise<void> {
  const meta = await readFile(path.join(catalogueDir, LED, 'meta.yaml'), 'utf8');
  const variantMeta = meta.replace(
    'slug: led-resistor-basic',
    `slug: ${slug}\nparent: ${parent}\nchangeSummary: Variant ${slug}`,
  );
  await mkdir(path.join(catalogueDir, 'led-resistor', slug), { recursive: true });
  await writeFile(path.join(catalogueDir, 'led-resistor', slug, 'meta.yaml'), variantMeta);
  await mkdir(path.join(renderDir, 'led-resistor', slug), { recursive: true });
  await writeFile(
    path.join(renderDir, 'led-resistor', slug, 'schematic.svg'),
    `<svg>${slug}</svg>`,
  );
}

beforeEach(async () => {
  root = await mkdtemp(path.join(tmpdir(), 'osh-import-'));
  catalogueDir = path.join(root, 'catalogue');
  renderDir = path.join(root, 'rendered');
  await cp(REAL_CATALOGUE, catalogueDir, { recursive: true });
  await mkdir(path.join(renderDir, LED), { recursive: true });
  await writeFile(path.join(renderDir, LED, 'schematic.svg'), '<svg>led</svg>');
  repository = new RecordingRepository();
});

afterEach(async () => {
  await rm(root, { recursive: true, force: true });
});

describe('importCatalogue', () => {
  it('publishes the real LED block with its rendered schematic', async () => {
    const result = await importCatalogue({ catalogueDir, renderDir, repository });

    expect(result).toEqual({
      ok: true,
      summary: { added: ['led-resistor-basic'], changed: [], unchanged: [], removed: [] },
    });
    expect(
      repository.mirrored?.map(({ block, svg }) => [
        block.slug,
        block.difficulty,
        block.specs.length,
        svg,
      ]),
    ).toEqual([['led-resistor-basic', 'BEGINNER', 5, '<svg>led</svg>']]);
  });

  it('publishes a variant even when its folder sorts before its parent', async () => {
    await addVariant('a-led-pair', 'led-resistor-basic');

    const result = await importCatalogue({ catalogueDir, renderDir, repository });

    expect(result.ok).toBe(true);
    expect(
      repository.mirrored?.find(({ block }) => block.slug === 'a-led-pair')?.block.parent?.slug,
    ).toBe('led-resistor-basic');
  });

  it('reports domain errors with the file to fix and writes nothing', async () => {
    await addVariant('orphan', 'missing-parent');

    const result = await importCatalogue({ catalogueDir, renderDir, repository });

    expect(result).toEqual({
      ok: false,
      errors: [
        {
          file: 'led-resistor/orphan/meta.yaml',
          field: 'parent',
          message: 'unknown parent block "missing-parent"',
        },
      ],
    });
    expect(repository.mirrored).toBeUndefined();
  });

  it('requires folder names to match the slug and the base circuit', async () => {
    await cp(
      path.join(catalogueDir, LED),
      path.join(catalogueDir, 'wrong-circuit', 'renamed-folder'),
      { recursive: true },
    );
    await cp(path.join(renderDir, LED), path.join(renderDir, 'wrong-circuit', 'renamed-folder'), {
      recursive: true,
    });

    const result = await importCatalogue({ catalogueDir, renderDir, repository });

    expect(result.ok ? [] : result.errors.map(({ file, field }) => `${file} ${field}`)).toEqual([
      'wrong-circuit/renamed-folder/meta.yaml slug',
      'wrong-circuit/renamed-folder/meta.yaml baseCircuit',
    ]);
    expect(repository.mirrored).toBeUndefined();
  });

  it('reports a block whose schematic was not rendered', async () => {
    await rm(path.join(renderDir, LED, 'schematic.svg'));

    const result = await importCatalogue({ catalogueDir, renderDir, repository });

    expect(
      result.ok ? [] : result.errors.map(({ file, message }) => [file, message.split(';')[0]]),
    ).toEqual([[`${LED}/meta.yaml`, `no rendered schematic in ${renderDir}/${LED}`]]);
  });

  it('reports invalid metadata with the file and field', async () => {
    const file = path.join(catalogueDir, LED, 'meta.yaml');
    await writeFile(
      file,
      (await readFile(file, 'utf8')).replace('ledCurrent: 13.6 mA', 'ledCurrent: 13.6 mAh'),
    );

    const result = await importCatalogue({ catalogueDir, renderDir, repository });

    expect(result).toEqual({
      ok: false,
      errors: [
        { file: `${LED}/meta.yaml`, field: 'specs.ledCurrent', message: 'unknown unit "mAh"' },
      ],
    });
  });

  it('reports a block folder without meta.yaml', async () => {
    await rm(path.join(catalogueDir, LED, 'meta.yaml'));

    const result = await importCatalogue({ catalogueDir, renderDir, repository });

    expect(result).toEqual({
      ok: false,
      errors: [{ file: `${LED}/meta.yaml`, field: '', message: 'missing meta.yaml' }],
    });
  });

  it('imports a block folder that is a symbolic link instead of skipping it', async () => {
    const real = path.join(root, 'elsewhere', 'led-resistor-basic');
    await mkdir(path.dirname(real), { recursive: true });
    await cp(path.join(catalogueDir, LED), real, { recursive: true });
    await rm(path.join(catalogueDir, LED), { recursive: true });
    await symlink(real, path.join(catalogueDir, LED));

    const result = await importCatalogue({ catalogueDir, renderDir, repository });

    expect(result.ok && result.summary.added).toEqual(['led-resistor-basic']);
  });

  it('reports a parent cycle in the files as a cycle', async () => {
    await addVariant('loop-a', 'loop-b');
    await addVariant('loop-b', 'loop-a');

    const result = await importCatalogue({ catalogueDir, renderDir, repository });

    expect(result).toEqual({
      ok: false,
      errors: [
        {
          file: 'led-resistor/loop-a/meta.yaml',
          field: 'parent',
          message: 'parent cycle among loop-a, loop-b',
        },
        {
          file: 'led-resistor/loop-b/meta.yaml',
          field: 'parent',
          message: 'parent cycle among loop-a, loop-b',
        },
      ],
    });
  });

  it('refuses to empty the database when no block is found', async () => {
    await rm(catalogueDir, { recursive: true });
    await mkdir(catalogueDir);

    const result = await importCatalogue({ catalogueDir, renderDir, repository });

    expect(result.ok ? '' : result.errors[0]?.message).toBe(
      'no block found; refusing to empty the database',
    );
    expect(repository.mirrored).toBeUndefined();
  });
});
