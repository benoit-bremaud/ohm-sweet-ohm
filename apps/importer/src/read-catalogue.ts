import { readdir, readFile, stat } from 'node:fs/promises';
import path from 'node:path';

import type { BlockDraft } from '@ohm-sweet-ohm/domain';
import { readBlockMeta } from '@ohm-sweet-ohm/schemas';

import { toDraft } from './to-draft.js';

/** A problem found in the catalogue files, located by the file the curator must fix. */
export interface ImportError {
  readonly file: string;
  readonly field: string;
  readonly message: string;
}

/** One block folder of the catalogue, read and checked, ready to be mirrored. */
export interface CatalogueEntry {
  readonly draft: BlockDraft;
  readonly svg: string;
  /** `<base-circuit>/<block>/meta.yaml`, for error messages. */
  readonly file: string;
}

/** Outcome of reading the catalogue: every entry, or every error across all folders. */
export type ReadResult =
  | { readonly ok: true; readonly entries: readonly CatalogueEntry[] }
  | { readonly ok: false; readonly errors: readonly ImportError[] };

/**
 * Reads every `<base-circuit>/<block>/meta.yaml` of the catalogue with its rendered SVG and
 * reports every problem: unreadable metadata, folder names that disagree with the metadata, or a
 * missing rendered schematic.
 */
export async function readCatalogue(catalogueDir: string, renderDir: string): Promise<ReadResult> {
  const entries: CatalogueEntry[] = [];
  const errors: ImportError[] = [];
  for (const baseDir of await subdirectories(catalogueDir)) {
    for (const blockDir of await subdirectories(path.join(catalogueDir, baseDir))) {
      // Sequential on purpose: a few folders, and the errors keep the catalogue order.
      const entry = await readBlock(catalogueDir, renderDir, baseDir, blockDir, errors); // NOSONAR (silences the whole line; meant for S9382)
      if (entry !== undefined) entries.push(entry);
    }
  }
  return errors.length > 0 ? { ok: false, errors } : { ok: true, entries };
}

/** Reads one block folder; every problem goes to `errors`, and an unusable folder yields nothing. */
async function readBlock(
  catalogueDir: string,
  renderDir: string,
  baseDir: string,
  blockDir: string,
  errors: ImportError[],
): Promise<CatalogueEntry | undefined> {
  const relativeDir = `${baseDir}/${blockDir}`;
  const file = `${relativeDir}/meta.yaml`;
  const metaText = await readOrUndefined(path.join(catalogueDir, file));
  if (metaText === undefined) {
    errors.push({ file, field: '', message: 'missing meta.yaml' });
    return undefined;
  }
  const meta = readBlockMeta(metaText);
  if (!meta.ok) {
    errors.push(...meta.errors.map((error) => ({ file, ...error })));
    return undefined;
  }
  if (meta.meta.slug !== blockDir) {
    errors.push({ file, field: 'slug', message: `must equal the folder name "${blockDir}"` });
  }
  if (meta.meta.baseCircuit !== baseDir) {
    errors.push({
      file,
      field: 'baseCircuit',
      message: `must equal the folder name "${baseDir}"`,
    });
  }
  const svg = await readOrUndefined(path.join(renderDir, relativeDir, 'schematic.svg'));
  if (svg === undefined) {
    errors.push({
      file,
      field: '',
      message: `no rendered schematic in ${renderDir}/${relativeDir}; run the renderer first`,
    });
    return undefined;
  }
  return { draft: toDraft(meta.meta, { relativeDir }), svg, file };
}

/**
 * Orders strings by UTF-16 code unit, as a bare `sort()` does: unlike `localeCompare`, the order
 * does not depend on the machine's locale, so the import order and its messages are reproducible.
 */
export function byCodeUnit(a: string, b: string): number {
  return Number(a > b) - Number(a < b);
}

/**
 * Directory names inside `dir`, following symbolic links: a linked block folder must be imported,
 * never silently skipped and then removed from the database by the mirror.
 */
async function subdirectories(dir: string): Promise<readonly string[]> {
  const items = await readdir(dir, { withFileTypes: true });
  const names: string[] = [];
  for (const item of items) {
    const isDirectory = item.isSymbolicLink()
      ? (await stat(path.join(dir, item.name))).isDirectory()
      : item.isDirectory();
    if (isDirectory) names.push(item.name);
  }
  return names.sort(byCodeUnit);
}

async function readOrUndefined(file: string): Promise<string | undefined> {
  try {
    return await readFile(file, 'utf8');
  } catch (error) {
    if (error instanceof Error && 'code' in error && error.code === 'ENOENT') return undefined;
    throw error;
  }
}
