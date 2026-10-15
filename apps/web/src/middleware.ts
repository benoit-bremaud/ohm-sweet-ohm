import { defineMiddleware } from 'astro:middleware';

// Headers a CSP <meta> cannot carry; the CSP itself comes from Astro's security.csp.
export const onRequest = defineMiddleware(async (_context, next) => {
  const response = await next();
  response.headers.set('x-content-type-options', 'nosniff');
  response.headers.set('x-frame-options', 'DENY');
  response.headers.set('referrer-policy', 'strict-origin-when-cross-origin');
  return response;
});
