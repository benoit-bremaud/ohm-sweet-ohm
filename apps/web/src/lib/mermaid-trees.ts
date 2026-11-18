import { createHash } from 'node:crypto';

// Shared by the site (remark plugin, tests) and `just trees` (scripts/render-trees.ts), which runs
// under Node type stripping: keep this module free of relative imports.

const BLOCK = /^```mermaid\n([\s\S]*?)^```$/gm;

/** The Mermaid blocks of a guide, in reading order, without their fences. */
export function mermaidBlocks(markdown: string): string[] {
  return [...markdown.matchAll(BLOCK)].map((m) => m[1] ?? '');
}

/** File, next to the guide, holding the rendering of its block `index` (0-based). */
export function treeFile(index: number): string {
  return `arbre-${String(index + 1)}.svg`;
}

/**
 * First line of a rendered tree: the hash of the Mermaid source it was drawn from, so a test can
 * tell a stale SVG from the guide without a browser.
 */
export function sourceMark(source: string): string {
  const hash = createHash('sha256').update(source).digest('hex').slice(0, 16);
  return `<!-- mermaid-source ${hash} -->`;
}
