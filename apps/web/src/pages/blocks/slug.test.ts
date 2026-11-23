import { experimental_AstroContainer as AstroContainer } from 'astro/container';
import { afterEach, beforeAll, describe, expect, it, vi } from 'vitest';

import { LED_BLOCK } from '../../lib/block.fixture';
import { type BlockLookup, findBlock } from '../../lib/catalogue';
import BlockPage from './[slug].astro';

// The page wires findBlock to the response (findBlock has its own tests); the Worker bindings
// do not exist under Node, so the runtime reader is replaced too.
vi.mock('../../lib/catalogue-runtime', () => ({ catalogueReader: {} }));
vi.mock('../../lib/catalogue', async (importOriginal) => ({
  ...(await importOriginal<typeof import('../../lib/catalogue')>()),
  findBlock: vi.fn(),
}));

function serve(lookup: BlockLookup): void {
  vi.mocked(findBlock).mockResolvedValue(lookup);
}

function found(block: Partial<typeof LED_BLOCK> = {}): BlockLookup {
  return { kind: 'found', block: { ...LED_BLOCK, ...block } };
}

let container: AstroContainer;

beforeAll(async () => {
  container = await AstroContainer.create();
});

afterEach(() => {
  vi.mocked(findBlock).mockReset();
});

describe('block page', () => {
  it('renders the block with its same-origin schematic', async () => {
    serve(found());

    const html = await container.renderToString(BlockPage, {
      params: { slug: 'led-resistor-basic' },
    });

    expect(html).toMatch(/<h1[^>]*>LED with current-limiting resistor<\/h1>/);
    // Served by this Worker (ADR-0005): a same-origin path, so img-src 'self' allows it.
    expect(html).toMatch(/<img[^>]+src="\/blocks\/led-resistor-basic\/schematic\.svg"/);
    expect(html).not.toContain('Hazardous voltage');
    expect(html).not.toContain('<script');
  });

  it('warns before the schematic when the block is hazardous', async () => {
    serve(found({ hazardous: true }));

    const html = await container.renderToString(BlockPage, {
      params: { slug: 'led-resistor-basic' },
    });

    expect(html.indexOf('Hazardous voltage')).toBeGreaterThan(0);
    expect(html.indexOf('Hazardous voltage')).toBeLessThan(html.indexOf('<img'));
  });

  it.each([
    ['theoretical', 'Theoretical'],
    ['tested', 'Tested on a build'],
  ] as const)('stamps a %s block with its validation status', async (status, label) => {
    serve(found({ validationStatus: status }));

    const html = await container.renderToString(BlockPage, {
      params: { slug: 'led-resistor-basic' },
    });

    expect(html).toMatch(new RegExp(`class="stamp ${status}[^"]*"[^>]*>\\s*${label}\\s*<`));
  });

  it('links the source only when it has a URL', async () => {
    serve(found({ source: { title: 'App note', url: 'https://example.com/an' } }));

    const html = await container.renderToString(BlockPage, {
      params: { slug: 'led-resistor-basic' },
    });

    expect(html).toContain('<a href="https://example.com/an"');
  });

  it('answers 502, not cacheable, when the catalogue is unavailable', async () => {
    serve({ kind: 'unavailable', reason: 'database down' });

    const response = await container.renderToResponse(BlockPage, { params: { slug: 'led' } });

    expect(response.status).toBe(502);
    expect(response.headers.get('cache-control')).toBe('no-store');
    expect(await response.text()).toContain('Catalogue unavailable');
  });
});
