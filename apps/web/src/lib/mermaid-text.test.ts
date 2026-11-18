import { describe, expect, it } from 'vitest';

import { DIAGRAM_ALT, diagramText, remarkMermaidImages } from './mermaid-text';

const code = (lang: string, value: string) => ({ type: 'code', lang, value });

describe('diagramText', () => {
  it('folds the steps under a summary, branches nested under their step', () => {
    expect(diagramText('flowchart TD\n  A[Un] -- oui --> B[Deux]')).toBe(
      '<details><summary>Version texte du schéma</summary><ol>' +
        '<li>Un<ul><li>oui → Deux</li></ul></li><li>Deux</li></ol></details>',
    );
  });

  it('escapes labels', () => {
    expect(diagramText('flowchart TD\n  A["<b>R & C</b>"]')).toContain(
      '<li>&lt;b&gt;R &amp; C&lt;/b&gt;</li>',
    );
  });
});

describe('remarkMermaidImages', () => {
  it('numbers the blocks of a file, nested ones included, and leaves other code alone', () => {
    const tree = {
      type: 'root',
      children: [
        code('mermaid', 'flowchart TD\n  A[Un] --> B[Deux]'),
        code('js', 'x'),
        { type: 'listItem', children: [code('mermaid', 'flowchart LR\n  C[Trois]')] },
      ],
    };
    remarkMermaidImages()(tree);

    expect(tree.children).toEqual([
      { type: 'paragraph', children: [{ type: 'image', url: 'arbre-1.svg', alt: DIAGRAM_ALT }] },
      { type: 'html', value: diagramText('flowchart TD\n  A[Un] --> B[Deux]') },
      code('js', 'x'),
      {
        type: 'listItem',
        children: [
          {
            type: 'paragraph',
            children: [{ type: 'image', url: 'arbre-2.svg', alt: DIAGRAM_ALT }],
          },
          { type: 'html', value: diagramText('flowchart LR\n  C[Trois]') },
        ],
      },
    ]);
  });
});
