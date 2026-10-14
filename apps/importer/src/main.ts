import path from 'node:path';

import { BlockRepository, createDatabase, migrateToLatest } from '@ohm-sweet-ohm/db';

import { importCatalogue } from './import-catalogue.js';

/**
 * Usage, from the repository root: DATABASE_URL=postgres://… pnpm catalogue:import [catalogueDir] [renderDir]
 * Run `pnpm catalogue:render` first; it writes the rendered SVGs to build/catalogue. Paths are
 * resolved from the directory where the command was launched (pnpm's INIT_CWD).
 */
async function main(): Promise<number> {
  const databaseUrl = process.env.DATABASE_URL;
  if (databaseUrl === undefined || databaseUrl === '') {
    console.error('DATABASE_URL is required');
    return 2;
  }
  const [catalogueArgument = 'catalogue', renderArgument = 'build/catalogue'] =
    process.argv.slice(2);
  const launchDir = process.env.INIT_CWD ?? process.cwd();
  const catalogueDir = path.resolve(launchDir, catalogueArgument);
  const renderDir = path.resolve(launchDir, renderArgument);
  const db = createDatabase(databaseUrl);
  try {
    await migrateToLatest(db);
    const result = await importCatalogue({
      catalogueDir,
      renderDir,
      repository: new BlockRepository(db),
    });
    if (!result.ok) {
      for (const error of result.errors) {
        console.error(
          `${error.file}${error.field === '' ? '' : ` ${error.field}`}: ${error.message}`,
        );
      }
      console.error(`import refused: ${String(result.errors.length)} error(s), database unchanged`);
      return 1;
    }
    const { added, changed, unchanged, removed } = result.summary;
    for (const [label, slugs] of [
      ['added', added],
      ['changed', changed],
      ['removed', removed],
    ] as const) {
      for (const slug of slugs) console.log(`${label}: ${slug}`);
    }
    console.log(
      `catalogue mirrored: ${String(added.length)} added, ${String(changed.length)} changed, ` +
        `${String(unchanged.length)} unchanged, ${String(removed.length)} removed`,
    );
    return 0;
  } catch (error) {
    console.error(`import failed: ${error instanceof Error ? error.message : String(error)}`);
    return 1;
  } finally {
    await db.destroy();
  }
}

process.exitCode = await main();
