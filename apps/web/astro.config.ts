import cloudflare from '@astrojs/cloudflare';
import { unified } from '@astrojs/markdown-remark';
import { defineConfig, envField } from 'astro/config';
import rehypeMermaid from 'rehype-mermaid';

import { rehypeGuideLinks } from './src/lib/guide-links';
import { rehypeMermaidText } from './src/lib/mermaid-text';

// Every page is rendered on demand so an import shows within the API's freshness window
// without a redeploy (ADR-0003).
export default defineConfig({
  output: 'server',
  // No image transformation and no sessions: the only image is the schematic served by the
  // API, so the adapter must not provision Images or KV bindings.
  adapter: cloudflare({ imageService: 'passthrough' }),
  session: false,
  // Troubleshooting guides (#123): Mermaid trees become SVG images at build time (headless
  // Chromium through Playwright), so the strict CSP needs no script and no inline style.
  markdown: {
    // The guides hold no code to colour, only Mermaid blocks; Shiki's inline styles break the CSP.
    syntaxHighlight: false,
    processor: unified({
      rehypePlugins: [
        rehypeGuideLinks,
        rehypeMermaidText,
        [rehypeMermaid, { strategy: 'img-svg', dark: true }],
      ],
    }),
  },
  env: {
    schema: {
      // Origin of the catalogue API, server-side only; validated at build and at start.
      API_URL: envField.string({ context: 'server', access: 'public', url: true }),
    },
  },
  // Astro hashes its own inline styles; the page adds the API origin for images at request time.
  security: {
    csp: {
      directives: [
        "default-src 'none'",
        "base-uri 'none'",
        "form-action 'none'",
        "font-src 'self'",
        "frame-ancestors 'none'",
      ],
    },
  },
});
