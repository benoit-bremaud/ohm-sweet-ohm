// `astro check` resolves .astro imports itself; tsc and typescript-eslint need this declaration
// to type the components that tests hand to the Container API.
declare module '*.astro' {
  import type { AstroComponentFactory } from 'astro/runtime/server/index.js';

  const Component: AstroComponentFactory;
  export default Component;
}

// The Worker's bindings (wrangler.jsonc), read through `cloudflare:workers` (ADR-0005).
declare module 'cloudflare:workers' {
  export const env: { readonly HYPERDRIVE: { readonly connectionString: string } };
}
