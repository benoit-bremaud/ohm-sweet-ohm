import { blockResponseSchema, type BlockResponse } from '@ohm-sweet-ohm/schemas';

/** Same rule as the API's route parameter: a slug is kebab-case, nothing else reaches the network. */
const SLUG = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

export type BlockLookup =
  | { readonly kind: 'found'; readonly block: BlockResponse }
  | { readonly kind: 'not-found' }
  // The reason is for the logs only; pages never show it.
  | { readonly kind: 'unavailable'; readonly reason: string };

export function isSlug(value: string): boolean {
  return SLUG.test(value);
}

/**
 * Reads one block from the API and checks it against the shared contract, so the page renders
 * either a valid block or an error page, never a half-trusted response.
 */
export async function fetchBlock(
  apiUrl: string,
  slug: string,
  fetchFn: typeof fetch = fetch,
): Promise<BlockLookup> {
  if (!isSlug(slug)) {
    return { kind: 'not-found' };
  }
  let response: Response;
  try {
    response = await fetchFn(new URL(`/blocks/${slug}`, apiUrl), {
      headers: { accept: 'application/json' },
    });
  } catch (error) {
    return { kind: 'unavailable', reason: `API unreachable: ${describe(error)}` };
  }
  if (response.status === 404) {
    return { kind: 'not-found' };
  }
  if (!response.ok) {
    return { kind: 'unavailable', reason: `API answered ${String(response.status)}` };
  }
  let body: unknown;
  try {
    body = await response.json();
  } catch (error) {
    return { kind: 'unavailable', reason: `API body is not JSON: ${describe(error)}` };
  }
  const parsed = blockResponseSchema.safeParse(body);
  if (!parsed.success) {
    return { kind: 'unavailable', reason: `API response off contract: ${parsed.error.message}` };
  }
  return { kind: 'found', block: parsed.data };
}

function describe(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}
