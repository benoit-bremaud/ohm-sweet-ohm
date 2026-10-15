import { cp, mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

import { PostgreSqlContainer, type StartedPostgreSqlContainer } from '@testcontainers/postgresql';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';

import { BASE_CIRCUITS } from '@ohm-sweet-ohm/domain';
import { BlockRepository, createDatabase, migrateToLatest } from '@ohm-sweet-ohm/db';

import { importCatalogue } from './import-catalogue.js';

const REAL_CATALOGUE = new URL('../../../catalogue', import.meta.url).pathname;
const LED = 'led-resistor/led-resistor-basic';

describe('catalogue import against PostgreSQL', () => {
  let container: StartedPostgreSqlContainer;
  let db: ReturnType<typeof createDatabase>;
  let repository: BlockRepository;
  let root: string;
  let catalogueDir: string;
  let renderDir: string;

  beforeAll(async () => {
    container = await new PostgreSqlContainer('postgres:17-alpine').start();
    db = createDatabase(container.getConnectionUri(), (error) => {
      throw error;
    });
    await migrateToLatest(db);
    repository = new BlockRepository(db);
    root = await mkdtemp(path.join(tmpdir(), 'osh-import-int-'));
    catalogueDir = path.join(root, 'catalogue');
    renderDir = path.join(root, 'rendered');
    await cp(REAL_CATALOGUE, catalogueDir, { recursive: true });
    await mkdir(path.join(renderDir, LED), { recursive: true });
    await writeFile(path.join(renderDir, LED, 'schematic.svg'), '<svg>led</svg>');
  }, 180_000);

  afterAll(async () => {
    await db.destroy();
    await container.stop();
    await rm(root, { recursive: true, force: true });
  });

  it('mirrors the real catalogue, is idempotent, and rewrites a changed schematic', async () => {
    const first = await importCatalogue({ catalogueDir, renderDir, repository });
    const second = await importCatalogue({ catalogueDir, renderDir, repository });
    const loaded = await repository.loadCatalogue(BASE_CIRCUITS);

    expect([first, second]).toEqual([
      {
        ok: true,
        summary: { added: ['led-resistor-basic'], changed: [], unchanged: [], removed: [] },
      },
      {
        ok: true,
        summary: { added: [], changed: [], unchanged: ['led-resistor-basic'], removed: [] },
      },
    ]);
    expect(loaded.findBlock('led-resistor-basic')?.specFor('ledColor')?.toRaw()).toEqual({
      key: 'ledColor',
      text: 'red',
    });

    await writeFile(path.join(renderDir, LED, 'schematic.svg'), '<svg>led v2</svg>');
    const third = await importCatalogue({ catalogueDir, renderDir, repository });
    expect(third).toEqual({
      ok: true,
      summary: { added: [], changed: ['led-resistor-basic'], unchanged: [], removed: [] },
    });
  });

  it('removes a block whose folder was deleted from the catalogue', async () => {
    const variant = path.join(catalogueDir, 'led-resistor', 'led-pair');
    await cp(path.join(catalogueDir, LED), variant, { recursive: true });
    const meta = path.join(variant, 'meta.yaml');
    await writeFile(
      meta,
      (await readFile(meta, 'utf8')).replace(
        'slug: led-resistor-basic',
        'slug: led-pair\nparent: led-resistor-basic\nchangeSummary: Two LEDs',
      ),
    );
    await cp(path.join(renderDir, LED), path.join(renderDir, 'led-resistor', 'led-pair'), {
      recursive: true,
    });
    const withVariant = await importCatalogue({ catalogueDir, renderDir, repository });

    await rm(variant, { recursive: true });
    const withoutVariant = await importCatalogue({ catalogueDir, renderDir, repository });

    expect(withVariant).toEqual({
      ok: true,
      summary: { added: ['led-pair'], changed: [], unchanged: ['led-resistor-basic'], removed: [] },
    });
    expect(withoutVariant).toEqual({
      ok: true,
      summary: { added: [], changed: [], unchanged: ['led-resistor-basic'], removed: ['led-pair'] },
    });
    expect((await repository.loadCatalogue(BASE_CIRCUITS)).findBlock('led-pair')).toBeUndefined();
  });
});
