import type { APIRoute } from 'astro';

/**
 * The troubleshooting guides are the site's main content until the home page of the redesign
 * (#161); a temporary redirect, so search engines keep `/` for that page (#111).
 */
export const GET: APIRoute = ({ redirect }) => redirect('/depannage/', 302);
