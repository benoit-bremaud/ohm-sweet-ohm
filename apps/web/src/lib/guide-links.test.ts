import { describe, expect, it } from 'vitest';

import { guideDir, rehypeGuideLinks, rewriteGuideHref } from './guide-links';

const REPO = 'https://github.com/benoit-bremaud/ohm-sweet-ohm/blob/main/troubleshooting';

describe('rewriteGuideHref', () => {
  it('maps a guide README to its route, from the menu and from another guide', () => {
    expect(rewriteGuideHref('00_securite/README.md', '')).toBe('/depannage/00_securite');
    expect(rewriteGuideHref('../02_pieges_en_circuit/README.md', '10_resistance')).toBe(
      '/depannage/02_pieges_en_circuit',
    );
  });

  it('keeps the anchor', () => {
    expect(rewriteGuideHref('../01_multimetre/README.md#mode-diode', '13_fusible')).toBe(
      '/depannage/01_multimetre#mode-diode',
    );
  });

  it('maps the menu README to the index', () => {
    expect(rewriteGuideHref('../README.md', '10_resistance')).toBe('/depannage');
  });

  it('sends other repository files to GitHub', () => {
    expect(rewriteGuideHref('gabarit.md', '')).toBe(`${REPO}/gabarit.md`);
    expect(rewriteGuideHref('../LICENSE', '10_resistance')).toBe(`${REPO}/LICENSE`);
  });

  it('leaves absolute URLs, anchors, root paths and figures alone', () => {
    for (const href of ['https://example.org/a.md', 'mailto:a@b.c', '#detail', '/x', 'f.svg', '']) {
      expect(rewriteGuideHref(href, '10_resistance')).toBe(href);
    }
  });

  it('refuses a link that leaves troubleshooting/', () => {
    expect(() => rewriteGuideHref('../../README.md', '10_resistance')).toThrow(/leaves/);
  });
});

describe('guideDir', () => {
  it('gives the folder under troubleshooting/', () => {
    expect(guideDir('/repo/troubleshooting/10_resistance/README.md')).toBe('10_resistance');
    expect(guideDir('/repo/troubleshooting/README.md')).toBe('');
    expect(guideDir('/elsewhere/README.md')).toBeUndefined();
  });
});

describe('rehypeGuideLinks', () => {
  const tree = () => ({
    type: 'root',
    children: [
      {
        type: 'element',
        tagName: 'p',
        children: [
          { type: 'element', tagName: 'a', properties: { href: '../00_securite/README.md' } },
          { type: 'element', tagName: 'img', properties: { src: 'a.svg' } },
        ],
      },
    ],
  });
  const firstHref = (t: ReturnType<typeof tree>) => t.children[0]?.children[0]?.properties.href;

  it('rewrites the links of a guide', () => {
    const t = tree();
    rehypeGuideLinks()(t, { path: '/repo/troubleshooting/10_resistance/README.md' });
    expect(firstHref(t)).toBe('/depannage/00_securite');
  });

  it('ignores Markdown outside troubleshooting/ and files without a path', () => {
    const outside = tree();
    rehypeGuideLinks()(outside, { path: '/repo/docs/README.md' });
    expect(firstHref(outside)).toBe('../00_securite/README.md');

    const noPath = tree();
    rehypeGuideLinks()(noPath, {});
    expect(firstHref(noPath)).toBe('../00_securite/README.md');
  });
});
