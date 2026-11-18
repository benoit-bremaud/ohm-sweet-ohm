// Renders every Mermaid block of the troubleshooting guides to a committed SVG next to its guide
// (`just trees`, #123). The site serves these files: no browser runs at build or deploy time.
import { readdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

import { createMermaidRenderer } from 'mermaid-isomorphic';

import { mermaidBlocks, sourceMark, treeFile } from '../src/lib/mermaid-trees.ts';

const root = new URL('../../../troubleshooting/', import.meta.url).pathname;
const render = createMermaidRenderer();
let written = 0;

for (const guide of readdirSync(root).filter((d) => /^\d\d_/.test(d))) {
  const dir = join(root, guide);
  for (const old of readdirSync(dir).filter((f) => /^arbre-\d+\.svg$/.test(f))) {
    rmSync(join(dir, old));
  }
  const blocks = mermaidBlocks(readFileSync(join(dir, 'README.md'), 'utf8'));
  // SVG text labels, not HTML ones: an <img> lays them out with the viewer's fonts otherwise.
  const results = await render(blocks, {
    mermaidConfig: { flowchart: { htmlLabels: false }, theme: 'neutral' },
  });
  results.forEach((result, i) => {
    if (result.status === 'rejected') {
      throw new Error(`${guide}, diagram ${String(i + 1)}: ${String(result.reason)}`);
    }
    writeFileSync(join(dir, treeFile(i)), `${sourceMark(blocks[i] ?? '')}\n${result.value.svg}\n`);
    written += 1;
  });
}

console.log(`trees: ${String(written)} SVG written under troubleshooting/`);
process.exit(0);
