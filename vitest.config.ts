import { defineConfig } from 'vitest/config';

// Floor of the pre-merge gate, applied to every package on its own so that a well-tested package
// cannot hide an untested one in the global figure.
const FLOOR = { lines: 80, functions: 80, branches: 80, statements: 80 };
// Every workspace package: a new one must be added here, or its code has no floor.
const PACKAGES = [
  'apps/api',
  'apps/importer',
  'apps/web',
  'packages/db',
  'packages/domain',
  'packages/schemas',
];

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
    coverage: {
      provider: 'v8',
      include: ['{apps,packages}/*/src/**/*.{ts,astro}'],
      // main.ts files only wire the process together; `just smoke` proves the api one starts.
      exclude: ['**/*.test.ts', '**/*.d.ts', '{apps,packages}/*/src/main.ts'],
      // lcov feeds SonarQube (sonar-project.properties).
      reporter: ['text-summary', 'text', 'lcov'],
      thresholds: Object.fromEntries(PACKAGES.map((p) => [`${p}/src/**`, FLOOR])),
    },
  },
});
