import { defineMiddleware } from 'astro:middleware';

/**
 * Hardening headers that Astro's security.csp does not emit; the CSP itself is sent as a header
 * on every on-demand page. HSTS is a deployment concern (issue #19). Prerendered pages never reach
 * this middleware: public/_headers repeats these headers for /depannage only;
 * a new prerendered route needs its own rule there.
 */
export const onRequest = defineMiddleware(async (_context, next) => {
  const response = await next();
  response.headers.set('x-content-type-options', 'nosniff');
  response.headers.set('x-frame-options', 'DENY');
  response.headers.set('referrer-policy', 'strict-origin-when-cross-origin');
  response.headers.set('permissions-policy', 'camera=(), microphone=(), geolocation=()');
  return response;
});
