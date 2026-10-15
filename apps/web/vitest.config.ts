import { fileURLToPath } from 'node:url';

import { getViteConfig } from 'astro/config';
// Augments Vite's UserConfig with the `test` field.
import 'vitest/config';

// Astro's Vite config lets tests render .astro components through the Container API, which
// needs a server environment since Astro 6. The root is explicit because the workspace runs
// this project from the repository root.
export default getViteConfig(
  { test: { name: 'web', environment: 'node', include: ['src/**/*.test.ts'] } },
  { root: fileURLToPath(new URL('.', import.meta.url)) },
);
