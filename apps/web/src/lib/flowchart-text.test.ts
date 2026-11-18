import { describe, expect, it } from 'vitest';

import { flowchartSteps } from './flowchart-text';

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

  it('shows the id of a node never labelled and ignores directives', () => {
    expect(flowchartSteps('flowchart LR\n  X --> Y\n  classDef a fill:#fff\n  end')).toEqual([
      { label: 'X', branches: [{ condition: undefined, to: 'Y' }] },
      { label: 'Y', branches: [] },
    ]);
  });

  it.each([
    ['a thick link', 'A ==> B'],
    ['a link without arrow', 'A --- B'],
    ['a pipe label', 'A -->|oui| B'],
  ])('refuses %s rather than dropping it', (_name, line) => {
    expect(() => flowchartSteps(`flowchart TD\n  ${line}`)).toThrow(/not understood/);
  });
});
