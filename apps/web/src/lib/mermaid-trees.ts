import { createHash } from 'node:crypto';

// Shared by the site (remark plugin, tests) and `just trees` (scripts/render-trees.ts), which runs
// under Node type stripping: keep this module free of relative imports.

/**
 * Mermaid settings of `just trees`. Labels are SVG text, not HTML in a foreignObject that an
 * <img> would lay out with the viewer's fonts; the root key, `flowchart.htmlLabels` is ignored.
 */
export const RENDER_CONFIG = { htmlLabels: false, theme: 'neutral' } as const;

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
 * First line of a rendered tree: the hash of the Mermaid source and of the render settings it was
 * drawn with, so a test can tell a stale SVG from the guide without a browser.
 */
export function sourceMark(source: string): string {
  const hash = createHash('sha256')
    .update(`${JSON.stringify(RENDER_CONFIG)}\n${source}`)
    .digest('hex')
    .slice(0, 16);
  return `<!-- mermaid-source ${hash} -->`;
}
