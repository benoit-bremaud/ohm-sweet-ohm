// Renders every Mermaid block of the troubleshooting guides to a committed SVG next to its guide
// (`just trees`, #123). The site serves these files: no browser runs at build or deploy time.
import { readdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { createMermaidRenderer } from 'mermaid-isomorphic';

import { RENDER_CONFIG, mermaidBlocks, sourceMark, treeFile } from '../src/lib/mermaid-trees.ts';

const root = fileURLToPath(new URL('../../../troubleshooting/', import.meta.url));
const render = createMermaidRenderer();
let written = 0;

for (const guide of readdirSync(root).filter((d) => /^\d\d_/.test(d))) {
  const dir = join(root, guide);
  for (const old of readdirSync(dir).filter((f) => /^arbre-\d+\.svg$/.test(f))) {
    rmSync(join(dir, old));
  }
  const blocks = mermaidBlocks(readFileSync(join(dir, 'README.md'), 'utf8'));
  const results = await render(blocks, { mermaidConfig: RENDER_CONFIG });
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
