import { experimental_AstroContainer as AstroContainer } from 'astro/container';
import { getCollection } from 'astro:content';
import { beforeAll, describe, expect, it } from 'vitest';

import GuidePage from './[guide].astro';
import GuidesIndex from './index.astro';

// The pages read the real guides of troubleshooting/: the content is the fixture.
let container: AstroContainer;

beforeAll(async () => {
  container = await AstroContainer.create();
});

describe('guides collection', () => {
  it('loads one entry per guide folder, menu excluded', async () => {
    const ids = (await getCollection('guides')).map((g) => g.id);
    expect(ids).toContain('10_resistance');
    expect(ids).not.toContain('menu');
    expect(ids.every((id) => /^\d\d_/.test(id))).toBe(true);
  });
});

describe('guides index', () => {
  it('renders the menu in French with the guides as site links', async () => {
    const html = await container.renderToString(GuidesIndex);

    expect(html).toMatch(/<html lang="fr"/);
    expect(html).toMatch(/<h1[^>]*>Dépannage électronique<\/h1>/);
    expect(html).toContain('href="/depannage/10_resistance"');
    expect(html).not.toContain('README.md');
  });
});

describe('guide page', () => {
  it('renders a guide with its title, figures, tree and text version', async () => {
    const guide = (await getCollection('guides')).find((g) => g.id === '10_resistance');
    if (guide === undefined) throw new Error('guide 10_resistance missing');

    const html = await container.renderToString(GuidePage, {
      params: { guide: guide.id },
      props: { guide },
    });

    expect(html).toMatch(/<title>10 Résistance · Ohm Sweet Ohm<\/title>/);
    expect(html).toContain('href="/depannage"');
    expect(html).toContain('href="/depannage/02_pieges_en_circuit"');
    expect(html).toMatch(/<img[^>]+alt="Lecture d/);
    expect(html).toMatch(/<img[^>]+alt="Arbre de décision/);
    expect(html).toContain("Version texte de l'arbre");
    expect(html).not.toContain('language-mermaid');
  });
});
