// `astro check` resolves .astro imports itself; tsc and typescript-eslint need this declaration
// to type the components that tests hand to the Container API.
declare module '*.astro' {
  import type { AstroComponentFactory } from 'astro/runtime/server/index.js';

  const Component: AstroComponentFactory;
  export default Component;
}
