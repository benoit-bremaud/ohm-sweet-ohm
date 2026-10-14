import { BASE_CIRCUITS, Catalogue } from '@ohm-sweet-ohm/domain';
import type { BlockRepository, MirrorSummary } from '@ohm-sweet-ohm/db';

import { type CatalogueEntry, type ImportError, readCatalogue } from './read-catalogue.js';

export type ImportResult =
  | { readonly ok: true; readonly summary: MirrorSummary }
  | { readonly ok: false; readonly errors: readonly ImportError[] };

export interface ImportOptions {
  readonly catalogueDir: string;
  readonly renderDir: string;
  readonly repository: Pick<BlockRepository, 'mirror'>;
}

/**
 * Mirrors the catalogue folder into the database (02-sequence-publish-blocks.md): reads every
 * file, publishes every draft into a new catalogue, and writes only when nothing failed.
 */
export async function importCatalogue({
  catalogueDir,
  renderDir,
  repository,
}: ImportOptions): Promise<ImportResult> {
  const read = await readCatalogue(catalogueDir, renderDir);
  if (!read.ok) {
    return read;
  }
  if (read.entries.length === 0) {
    return {
      ok: false,
      errors: [
        {
          file: catalogueDir,
          field: '',
          message: 'no block found; refusing to empty the database',
        },
      ],
    };
  }

  const catalogue = new Catalogue(BASE_CIRCUITS);
  const errors = publishInWaves(catalogue, read.entries);
  if (errors.length > 0) {
    return { ok: false, errors };
  }

  const blocks = read.entries.map((entry) => {
    const block = catalogue.findBlock(entry.draft.slug);
    if (block === undefined) throw new Error(`published block ${entry.draft.slug} not found`);
    return { block, svg: entry.svg };
  });
  return { ok: true, summary: await repository.mirror(blocks) };
}

/**
 * Publishes drafts in waves: each wave takes the drafts whose parent is not waiting to be
 * published (already published, or absent so the domain reports it). Drafts left when a wave is
 * empty form parent cycles and are reported as such.
 */
function publishInWaves(catalogue: Catalogue, entries: readonly CatalogueEntry[]): ImportError[] {
  const errors: ImportError[] = [];
  let pending = [...entries];
  while (pending.length > 0) {
    const waiting = new Set(pending.map((entry) => entry.draft.slug));
    const wave = pending.filter(
      (entry) => entry.draft.parentSlug === undefined || !waiting.has(entry.draft.parentSlug),
    );
    if (wave.length === 0) {
      const cycle = pending
        .map((entry) => entry.draft.slug)
        .sort()
        .join(', ');
      errors.push(
        ...pending.map((entry) => ({
          file: entry.file,
          field: 'parent',
          message: `parent cycle among ${cycle}`,
        })),
      );
      break;
    }
    for (const entry of wave) {
      for (const error of catalogue.publish(entry.draft)) {
        errors.push({ file: entry.file, field: error.field, message: error.message });
      }
    }
    const published = new Set(wave.map((entry) => entry.draft.slug));
    pending = pending.filter((entry) => !published.has(entry.draft.slug));
  }
  return errors;
}
