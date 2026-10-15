import { experimental_AstroContainer as AstroContainer } from 'astro/container';
import { afterEach, beforeAll, describe, expect, it, vi } from 'vitest';

import { LED_BLOCK } from '../../lib/block.fixture';
import BlockPage from './[slug].astro';

// The page wires fetchBlock to the response: these tests stub the network, the one boundary.
function serve(status: number, body: unknown): void {
  vi.stubGlobal(
    'fetch',
    vi.fn(() => Promise.resolve(Response.json(body, { status }))),
  );
}

let container: AstroContainer;

beforeAll(async () => {
  container = await AstroContainer.create();
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('block page', () => {
  it('renders the block with its schematic from the API', async () => {
    serve(200, LED_BLOCK);

    const html = await container.renderToString(BlockPage, {
      params: { slug: 'led-resistor-basic' },
    });

    expect(html).toMatch(/<h1[^>]*>LED with current-limiting resistor<\/h1>/);
    // The origin comes from API_URL (wrangler vars or .dev.vars); the path is the contract.
    expect(html).toMatch(
      /<img[^>]+src="http:\/\/[^/]+\/blocks\/led-resistor-basic\/schematic\.svg"/,
    );
    expect(html).not.toContain('Hazardous voltage');
    expect(html).not.toContain('<script');
    // No link to a route that does not exist yet (home page comes with M2).
    expect(html).not.toMatch(/href="\/"/);
  });

  it('warns before the schematic when the block is hazardous', async () => {
    serve(200, { ...LED_BLOCK, hazardous: true });

    const html = await container.renderToString(BlockPage, {
      params: { slug: 'led-resistor-basic' },
    });

    expect(html.indexOf('Hazardous voltage')).toBeGreaterThan(0);
    expect(html.indexOf('Hazardous voltage')).toBeLessThan(html.indexOf('<img'));
  });

  it('links the source only when it has a URL', async () => {
    serve(200, { ...LED_BLOCK, source: { title: 'App note', url: 'https://example.com/an' } });

    const html = await container.renderToString(BlockPage, {
      params: { slug: 'led-resistor-basic' },
    });

    expect(html).toContain('<a href="https://example.com/an"');
  });

  it('answers 502, not cacheable, when the API fails', async () => {
    serve(500, { error: 'boom' });

    const response = await container.renderToResponse(BlockPage, { params: { slug: 'led' } });

    expect(response.status).toBe(502);
    expect(response.headers.get('cache-control')).toBe('no-store');
    expect(await response.text()).toContain('Catalogue unavailable');
  });
});
