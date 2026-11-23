import type { APIRoute } from 'astro';

import { catalogueReader } from '../../../lib/catalogue-runtime';
import { schematicResponse } from '../../../lib/schematic-response';

/** The block's rendered schematic, served from the catalogue database (ADR-0005). */
export const GET: APIRoute = ({ params, request }) =>
  schematicResponse(catalogueReader, params.slug ?? '', request.headers.get('if-none-match'));
