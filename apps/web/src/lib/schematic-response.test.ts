import { describe, expect, it, vi } from 'vitest';

import { schematicResponse } from './schematic-response';

const SVG = '<svg xmlns="http://www.w3.org/2000/svg"><text>LED</text></svg>';

const reader = {
  findSchematic: vi.fn((slug: string) =>
    Promise.resolve(
      slug === 'led-resistor-basic' ? { svg: SVG, contentHash: 'abc123' } : undefined,
    ),
  ),
};

describe('schematicResponse', () => {
  it('serves the SVG with a hash ETag and headers that forbid running code', async () => {
    const response = await schematicResponse(reader, 'led-resistor-basic', null);

    expect(response.status).toBe(200);
    expect(await response.text()).toBe(SVG);
    expect(Object.fromEntries(response.headers)).toMatchObject({
      'content-type': 'image/svg+xml; charset=utf-8',
      etag: '"abc123"',
      'x-content-type-options': 'nosniff',
      'cache-control': 'public, no-cache',
      'content-security-policy': "default-src 'none'; style-src 'unsafe-inline'; sandbox",
    });
  });

  it.each(['"abc123"', '"old", "abc123"', 'W/"abc123"', '*'])(
    'answers 304 without a body when If-None-Match is %s',
    async (ifNoneMatch) => {
      const response = await schematicResponse(reader, 'led-resistor-basic', ifNoneMatch);

      expect(response.status).toBe(304);
      expect(response.headers.get('etag')).toBe('"abc123"');
      expect(await response.text()).toBe('');
    },
  );

  it('sends the SVG again when the ETag is stale', async () => {
    const response = await schematicResponse(reader, 'led-resistor-basic', '"old"');

    expect(response.status).toBe(200);
  });

  it('answers 404 when the block has no schematic', async () => {
    const response = await schematicResponse(reader, 'led-pair', null);

    expect(response.status).toBe(404);
  });

  it('answers 404 for a malformed slug without reading the database', async () => {
    reader.findSchematic.mockClear();

    const response = await schematicResponse(reader, '../etc', null);

    expect(response.status).toBe(404);
    expect(reader.findSchematic).not.toHaveBeenCalled();
  });

  it('lets a database failure through, so Astro answers 500', async () => {
    const failing = { findSchematic: () => Promise.reject(new Error('down')) };

    await expect(schematicResponse(failing, 'led-resistor-basic', null)).rejects.toThrow('down');
  });
});
