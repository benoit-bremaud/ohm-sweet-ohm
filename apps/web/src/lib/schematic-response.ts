import { type CatalogueReader, isSlug } from './catalogue';

/**
 * SVGs are served as images that can never run code, even if a future contributed schematic
 * carried a script: no script, no plugin, sandboxed, and no MIME sniffing.
 */
const SVG_HEADERS = {
  'content-type': 'image/svg+xml; charset=utf-8',
  'content-security-policy': "default-src 'none'; style-src 'unsafe-inline'; sandbox",
  'x-content-type-options': 'nosniff',
  // Kept by caches but revalidated every time (a cheap 304), so an import shows at once.
  'cache-control': 'public, no-cache',
} as const;

/**
 * Answers GET /blocks/:slug/schematic.svg: the SVG with its content hash as ETag, 304 when the
 * client already holds it, 404 for a malformed slug or a block without schematic. A database
 * failure throws: Astro answers 500.
 */
export async function schematicResponse(
  reader: Pick<CatalogueReader, 'findSchematic'>,
  slug: string,
  ifNoneMatch: string | null,
): Promise<Response> {
  const schematic = isSlug(slug) ? await reader.findSchematic(slug) : undefined;
  if (schematic === undefined) {
    return new Response('not found', { status: 404, headers: { 'content-type': 'text/plain' } });
  }
  const etag = `"${schematic.contentHash}"`;
  const headers = { ...SVG_HEADERS, etag };
  if (matchesEtag(ifNoneMatch, etag)) {
    return new Response(null, { status: 304, headers });
  }
  return new Response(schematic.svg, { status: 200, headers });
}

/** RFC 9110 weak comparison: a list of tags, possibly weak (proxies add W/), or "*". */
function matchesEtag(ifNoneMatch: string | null, etag: string): boolean {
  return (
    ifNoneMatch?.split(',').some((tag) => {
      const candidate = tag.trim();
      return candidate === '*' || candidate.replace(/^W\//, '') === etag;
    }) ?? false
  );
}
