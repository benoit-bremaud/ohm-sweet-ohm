import cloudflare from '@astrojs/cloudflare';
import { unified } from '@astrojs/markdown-remark';
import { defineConfig } from 'astro/config';

import { rehypeGuideLinks } from './src/lib/guide-links';
import { remarkMermaidImages } from './src/lib/mermaid-text';

// Catalogue pages are rendered on demand from the catalogue database (Hyperdrive, ADR-0005) so an
// import shows within the cache's freshness window without a redeploy (ADR-0003). The troubleshooting guides under /depannage are prerendered:
// they change with a commit, not with an import (#123).
export default defineConfig({
  output: 'server',
  // pg is CommonJS and requires Node built-ins by their bare names ("events", "net"); the Worker's
  // ESM bundle has no `require`, so each server chunk gets one from node:module (workerd resolves
  // built-ins only and has no import.meta.url, hence the "/" base; #111).
  vite: {
    environments: {
      ssr: {
        build: {
          rollupOptions: {
            output: {
              banner:
                "import { createRequire as __osoCreateRequire } from 'node:module'; const require = __osoCreateRequire('/');",
            },
          },
        },
      },
    },
  },
  // No image transformation and no sessions: images are served as they are (the catalogue's schematics,
  // the guides' SVG figures), so the adapter must not provision Images or KV bindings.
  adapter: cloudflare({ imageService: 'passthrough' }),
  session: false,
  // The guide tests read the content store the dev server writes to .astro/; sync and build write
  // it there too, so a fresh checkout runs them after one `astro sync`
  // (`just sync`, run by `just setup`, `lint` and `test`).
  cacheDir: './.astro',
  // Troubleshooting guides (#123): each Mermaid block becomes the SVG `just trees` committed next
  // to its guide, plus a text version; no browser runs at build time and the CSP stays strict.
  // Rehype and remark plugins need the unified processor since Astro 7: @astrojs/markdown-remark is
  // pinned at 7.3.5 to share @astrojs/internal-helpers with astro 7.4.5 (7.3.9 breaks astro check).
  markdown: {
    // The guides hold no code to colour, only Mermaid blocks; Shiki's inline styles break the CSP.
    syntaxHighlight: false,
    processor: unified({
      remarkPlugins: [remarkMermaidImages],
      rehypePlugins: [rehypeGuideLinks],
    }),
  },
  // Astro hashes its own inline styles; the page layout adds img-src 'self'.
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
