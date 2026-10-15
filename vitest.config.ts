import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    projects: [
      {
        test: {
          name: 'node',
          include: ['{apps,packages}/*/src/**/*.test.ts'],
          exclude: ['apps/web/**', '**/node_modules/**'],
        },
      },
      // The web app needs Astro's Vite config to render components in tests.
      './apps/web/vitest.config.ts',
    ],
  },
});
