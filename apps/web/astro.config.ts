import cloudflare from '@astrojs/cloudflare';
import { defineConfig, envField } from 'astro/config';

// Every page is rendered on demand so an import shows within the API's freshness window
// without a redeploy (ADR-0003).
export default defineConfig({
  output: 'server',
  // No image transformation and no sessions: the only image is the schematic served by the
  // API, so the adapter must not provision Images or KV bindings.
  adapter: cloudflare({ imageService: 'passthrough' }),
  session: false,
  env: {
    schema: {
      // Origin of the catalogue API, server-side only; validated at build and at start.
      API_URL: envField.string({ context: 'server', access: 'public', url: true }),
    },
  },
  // Astro hashes its own inline styles; the page adds the API origin for images at request time.
  security: {
    csp: {
      directives: ["default-src 'none'", "base-uri 'none'", "form-action 'none'"],
    },
  },
});
