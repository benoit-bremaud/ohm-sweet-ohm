import { readdirSync, readFileSync } from 'node:fs';

import { describe, expect, it } from 'vitest';

import { flowchartSteps } from './flowchart-text';
import { mermaidBlocks, sourceMark, treeFile } from './mermaid-trees';

describe('mermaidBlocks', () => {
  it('returns the Mermaid sources in order, other fences excluded', () => {
    const md = '```mermaid\nflowchart TD\n  A\n```\n\n```js\nx\n```\n\n```mermaid\ngraph LR\n```\n';
    expect(mermaidBlocks(md)).toEqual(['flowchart TD\n  A\n', 'graph LR\n']);
  });
});

describe('sourceMark', () => {
  it('changes with the source', () => {
    expect(sourceMark('a')).toMatch(/^<!-- mermaid-source [0-9a-f]{16} -->$/);
    expect(sourceMark('a')).not.toBe(sourceMark('b'));
  });
});

// The guides are the fixture: every diagram must have its committed, up-to-date SVG and a text
// version that reads every link. A failure here means: run `just trees`, or fix the guide.
describe('the diagrams of the guides', () => {
  const root = new URL('../../../../troubleshooting/', import.meta.url);
  const guides = readdirSync(root).filter((d) => /^\d\d_/.test(d));
  const read = (guide: string, file: string) =>
    readFileSync(new URL(`${guide}/${file}`, root), 'utf8');

  it('gives every guide at least one diagram', () => {
    expect(guides.filter((g) => mermaidBlocks(read(g, 'README.md')).length === 0)).toEqual([]);
  });

  it.each(guides)('%s: one current SVG per diagram, no orphan', (guide) => {
    const blocks = mermaidBlocks(read(guide, 'README.md'));
    const svgs = readdirSync(new URL(guide, root)).filter((f) => /^arbre-\d+\.svg$/.test(f));

    expect(svgs.sort()).toEqual(blocks.map((_, i) => treeFile(i)).sort());
    blocks.forEach((source, i) => {
      expect(read(guide, treeFile(i)).split('\n')[0]).toBe(sourceMark(source));
    });
  });

  it.each(guides)('%s: the text version reads every link and label', (guide) => {
    for (const source of mermaidBlocks(read(guide, 'README.md'))) {
      const links = source.split('\n').filter((l) => /-->|\.->/.test(l)).length;
      const steps = flowchartSteps(source);
      expect(steps.reduce((n, s) => n + s.branches.length, 0)).toBe(links);
      // A step showing a bare node id means a label was missed.
      const ids = new Set(source.match(/\b[A-Za-z0-9_]+(?=\s*[[{(])/g));
      expect(steps.filter((s) => ids.has(s.label))).toEqual([]);
    }
  });
});
