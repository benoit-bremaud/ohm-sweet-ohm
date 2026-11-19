import { experimental_AstroContainer as AstroContainer } from 'astro/container';
import { getCollection } from 'astro:content';
import { existsSync, readdirSync } from 'node:fs';

import { beforeAll, describe, expect, it } from 'vitest';

import { guidePaths, guideTitle } from '../../lib/guide-pages';
import { DIAGRAM_ALT } from '../../lib/mermaid-text';
import GuidePage from './[guide].astro';
import GuidesIndex from './index.astro';

// The pages read the real guides of troubleshooting/: the content is the fixture.
let container: AstroContainer;
let ids: string[];

beforeAll(async () => {
  container = await AstroContainer.create();
  ids = (await getCollection('guides')).map((g) => g.id);
});

const renderGuide = async (id: string) => {
  const path = (await guidePaths()).find((p) => p.params.guide === id);
  if (path === undefined) throw new Error(`no page for ${id}`);
  return container.renderToString(GuidePage, { params: path.params, props: path.props });
};

/** Every site link of a page must reach the index or an existing guide. */
const deadLinks = (html: string) =>
  [...html.matchAll(/href="\/depannage(?:\/([^"#?]+))?/g)]
    .map((m) => m[1])
    .filter((target) => target !== undefined && !ids.includes(target));

describe('guide pages', () => {
  it('has one prerendered path per guide folder, menu excluded', async () => {
    const paths = await guidePaths();
    expect(paths.map((p) => p.params.guide)).toEqual(ids);
    expect(ids).toContain('10_resistance');
    // instrument pages (#84) live in i-prefixed folders beside the numbered guides
    expect(ids).toContain('i1_multimetre');
    expect(ids).toContain('i2_oscilloscope');
    expect(ids).not.toContain('menu');
  });

  it('loads every folder holding a README, so a misnamed guide fails here', () => {
    const root = new URL('../../../../../troubleshooting/', import.meta.url);
    const folders = readdirSync(root, { withFileTypes: true })
      .filter((d) => d.isDirectory() && existsSync(new URL(`${d.name}/README.md`, root)))
      .map((d) => d.name);
    expect([...ids].sort()).toEqual(folders.sort());
  });

  it('takes the level 1 heading as title and refuses a guide without one', () => {
    expect(
      guideTitle(
        [
          { depth: 2, slug: 'a', text: 'A' },
          { depth: 1, slug: 'b', text: 'B' },
        ],
        'x',
      ),
    ).toBe('B');
    expect(() => guideTitle([], '99_vide')).toThrow(/99_vide/);
  });
});

describe('guides index', () => {
  it('renders the menu in French, every link on a guide', async () => {
    const html = await container.renderToString(GuidesIndex);

    expect(html).toMatch(/<html lang="fr"/);
    expect(html).toContain('href="/depannage/10_resistance"');
    expect(html).toContain('href="/depannage/i1_multimetre"');
    expect(html).toContain('href="/depannage/i2_oscilloscope"');
    expect(html).not.toContain('README.md');
    expect(deadLinks(html)).toEqual([]);
    for (const id of ids) expect(html, id).toContain(`href="/depannage/${id}"`);
  });
});

describe('guide page', () => {
  it('renders the diagram as an image with a text version', async () => {
    const html = await renderGuide('10_resistance');

    expect(html).toContain('href="/depannage"');
    // Vite inlines the SVG in tests; the file name is checked by remarkMermaidImages' own test.
    expect(html).toContain(`alt="${DIAGRAM_ALT.replace("'", '&#39;')}"`);
    expect(html).toContain('Version texte du schéma');
    expect(html).not.toContain('language-mermaid');
  });

  it('checks each guide: alt on every image, every site link alive', async () => {
    for (const id of ids) {
      const html = await renderGuide(id);
      expect(html, id).not.toMatch(/<img(?![^>]*\balt="[^"]+")[^>]*>/);
      expect(deadLinks(html), id).toEqual([]);
    }
  });
});
