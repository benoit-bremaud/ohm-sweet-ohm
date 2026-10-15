import { build } from 'esbuild';

/**
 * Bundles the API for the container image (ADR-0004): the workspace packages ship TypeScript
 * source, so they are bundled in; npm packages stay external and are installed in the image,
 * because `@fastify/swagger-ui` serves files from its own package directory and `pg` loads an
 * optional native binding at runtime.
 */
await build({
  entryPoints: ['src/main.ts'],
  outfile: 'dist/main.js',
  bundle: true,
  platform: 'node',
  format: 'esm',
  target: 'node22',
  sourcemap: true,
  logLevel: 'info',
  plugins: [
    {
      name: 'npm-external',
      setup(pluginBuild) {
        pluginBuild.onResolve({ filter: /^[^./]/ }, (args) =>
          args.path.startsWith('@ohm-sweet-ohm/') ? undefined : { path: args.path, external: true },
        );
      },
    },
  ],
});
