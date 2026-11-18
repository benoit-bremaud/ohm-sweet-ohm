import { readdirSync, readFileSync } from 'node:fs';

import { describe, expect, it } from 'vitest';

import { flowchartSteps } from './flowchart-text';
import { TREE_ALT, rehypeMermaidText, treeText } from './mermaid-text';

const TREE = `flowchart TD
  A[Résistance suspecte] --> B{Carbonisée ?}
  B -- oui --> C[Chercher le court-circuit<br/>en aval]
  B -- non --> D
  D(Mesurer hors tension)
  C -.-> E["Remplacer"]
  D -. si doute .-> A`;

describe('flowchartSteps', () => {
  it('lists every step in source order with its labelled and plain branches', () => {
    expect(flowchartSteps(TREE)).toEqual([
      { label: 'Résistance suspecte', branches: [{ condition: undefined, to: 'Carbonisée ?' }] },
      {
        label: 'Carbonisée ?',
        branches: [
          { condition: 'oui', to: 'Chercher le court-circuit en aval' },
          { condition: 'non', to: 'Mesurer hors tension' },
        ],
      },
      {
        label: 'Chercher le court-circuit en aval',
        branches: [{ condition: undefined, to: 'Remplacer' }],
      },
      {
        label: 'Mesurer hors tension',
        branches: [{ condition: 'si doute', to: 'Résistance suspecte' }],
      },
      { label: 'Remplacer', branches: [] },
    ]);
  });

  it('shows the id of a node never labelled and ignores other lines', () => {
    expect(flowchartSteps('flowchart LR\n  X --> Y\n  classDef a fill:#fff')).toEqual([
      { label: 'X', branches: [{ condition: undefined, to: 'Y' }] },
      { label: 'Y', branches: [] },
    ]);
  });
});

describe('rehypeMermaidText', () => {
  const tree = (lang: string) => ({
    type: 'root',
    children: [
      {
        type: 'element',
        tagName: 'pre',
        properties: {},
        children: [
          {
            type: 'element',
            tagName: 'code',
            properties: { className: [lang] },
            children: [{ type: 'text', value: 'flowchart TD\n  A[Un] --> B[Deux]' }],
          },
        ],
      },
    ],
  });

  it('adds the accessible description and a text version after a Mermaid block', () => {
    const t = tree('language-mermaid');
    rehypeMermaidText()(t);

    const code = t.children[0]?.children[0];
    expect(code?.children[0]).toEqual({
      type: 'text',
      value: `flowchart TD\n  accDescr: ${TREE_ALT}\n  A[Un] --> B[Deux]`,
    });
    expect(t.children[1]).toEqual(treeText('flowchart TD\n  A[Un] --> B[Deux]'));
  });

  it('leaves other code blocks alone', () => {
    const t = tree('language-js');
    rehypeMermaidText()(t);
    expect(t.children).toHaveLength(1);
  });
});

describe('treeText', () => {
  it('folds the steps under a summary, branches nested under their step', () => {
    const details = treeText('flowchart TD\n  A[Un] -- oui --> B[Deux]');
    expect(JSON.stringify(details)).toContain("Version texte de l'arbre");
    expect(JSON.stringify(details)).toContain('oui → Deux');
  });
});

describe('the trees of the guides', () => {
  const root = new URL('../../../../troubleshooting/', import.meta.url);
  const trees = readdirSync(root, { withFileTypes: true })
    .filter((d) => d.isDirectory())
    .flatMap((d) => {
      const md = readFileSync(new URL(`${d.name}/README.md`, root), 'utf8');
      return [...md.matchAll(/```mermaid\n([\s\S]*?)```/g)].map(
        (m) => [d.name, m[1] ?? ''] as const,
      );
    });

  it('finds at least one tree per guide family', () => {
    expect(trees.length).toBeGreaterThanOrEqual(13);
  });

  it.each(trees)('reads every arrow of the tree in %s', (_guide, source) => {
    const arrows = source.split('\n').filter((l) => /-->|\.->/.test(l)).length;
    const steps = flowchartSteps(source);
    expect(steps.reduce((n, s) => n + s.branches.length, 0)).toBe(arrows);
    // A step showing a bare node id means a label was missed.
    const ids = new Set(source.match(/\b[A-Za-z0-9_]+(?=\s*[[{(])/g));
    expect(steps.filter((s) => ids.has(s.label))).toEqual([]);
  });
});
