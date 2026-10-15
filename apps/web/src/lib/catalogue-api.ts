import { blockResponseSchema, SLUG_PATTERN, type BlockResponse } from '@ohm-sweet-ohm/schemas';

/**
 * Outcome of a block lookup: `not-found` covers a malformed slug and an API 404 (the 404 page);
 * `unavailable` covers network errors, non-2xx answers, non-JSON bodies and contract drift (the
 * 502 page). The reason is for the logs only; pages never show it.
 */
export type BlockLookup =
  | { readonly kind: 'found'; readonly block: BlockResponse }
  | { readonly kind: 'not-found' }
  | { readonly kind: 'unavailable'; readonly reason: string };

/** True for a kebab-case slug, the catalogue's one rule; anything else never reaches the network. */
export function isSlug(value: string): boolean {
  return SLUG_PATTERN.test(value);
}

/**
 * Reads one block from the API and checks it against the shared contract, so the page renders
 * either a valid block or an error page, never a half-trusted response. `apiUrl` is an origin;
 * a path in it is ignored.
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
    response = await fetchFn(new URL(`/blocks/${slug}`, new URL(apiUrl).origin), {
      headers: { accept: 'application/json' },
    });
  } catch (error) {
    return { kind: 'unavailable', reason: `API unreachable: ${messageOf(error)}` };
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
    return { kind: 'unavailable', reason: `API body is not JSON: ${messageOf(error)}` };
  }
  const parsed = blockResponseSchema.safeParse(body);
  if (!parsed.success) {
    return { kind: 'unavailable', reason: `API response off contract: ${parsed.error.message}` };
  }
  return { kind: 'found', block: parsed.data };
}

function messageOf(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}
