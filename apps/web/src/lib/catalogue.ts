import type { Catalogue } from '@ohm-sweet-ohm/domain';
import { blockResponseSchema, SLUG_PATTERN, type BlockResponse } from '@ohm-sweet-ohm/schemas';

import { toBlockResponse } from './to-block-response';

/** A rendered schematic and the hash of its content, used as the ETag. */
export interface Schematic {
  readonly svg: string;
  readonly contentHash: string;
}

/** What the pages read from the catalogue database (ADR-0005); injected so tests run without it. */
export interface CatalogueReader {
  catalogue(): Promise<Catalogue>;
  findSchematic(slug: string): Promise<Schematic | undefined>;
}

/**
 * Outcome of a block lookup: `not-found` covers a malformed slug and an unknown block (the 404
 * page); `unavailable` covers a database failure and a block that breaks the shared contract (the
 * 502 page). The reason is for the logs only; pages never show it.
 */
export type BlockLookup =
  | { readonly kind: 'found'; readonly block: BlockResponse }
  | { readonly kind: 'not-found' }
  | { readonly kind: 'unavailable'; readonly reason: string };

/** True for a kebab-case slug, the catalogue's one rule; anything else never reaches the database. */
export function isSlug(value: string): boolean {
  return SLUG_PATTERN.test(value);
}

/**
 * Reads one block and checks it against the shared contract, so the page renders either a valid
 * block or an error page, never a half-trusted one (a `javascript:` source link is refused).
 */
export async function findBlock(reader: CatalogueReader, slug: string): Promise<BlockLookup> {
  if (!isSlug(slug)) {
    return { kind: 'not-found' };
  }
  let catalogue: Catalogue;
  try {
    catalogue = await reader.catalogue();
  } catch (error) {
    return { kind: 'unavailable', reason: `catalogue unreachable: ${messageOf(error)}` };
  }
  const block = catalogue.findBlock(slug);
  if (block === undefined) {
    return { kind: 'not-found' };
  }
  const parsed = blockResponseSchema.safeParse(toBlockResponse(block));
  if (!parsed.success) {
    return { kind: 'unavailable', reason: `block off contract: ${parsed.error.message}` };
  }
  return { kind: 'found', block: parsed.data };
}

function messageOf(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}
