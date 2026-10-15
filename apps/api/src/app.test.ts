import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import type { FastifyInstance } from 'fastify';

import { blockResponseSchema } from '@ohm-sweet-ohm/schemas';

import { buildApp } from './app.js';
import { makeCatalogue } from './test-catalogue.js';

const SVG = '<svg xmlns="http://www.w3.org/2000/svg"><text>LED</text></svg>';

let app: FastifyInstance;

beforeEach(async () => {
  const catalogue = makeCatalogue();
  app = await buildApp({
    catalogue: { get: () => Promise.resolve(catalogue) },
    schematics: {
      findSchematic: (slug) =>
        Promise.resolve(
          slug === 'led-resistor-basic' ? { svg: SVG, contentHash: 'abc123' } : undefined,
        ),
    },
  });
});

afterEach(async () => {
  await app.close();
});

describe('GET /blocks/:slug', () => {
  it('should return a variant with lowercase values, SI units and its path', async () => {
    const response = await app.inject({ method: 'GET', url: '/blocks/led-pair' });

    const body = blockResponseSchema.parse(response.json());
    expect(response.statusCode).toBe(200);
    expect(body).toMatchObject({
      slug: 'led-pair',
      changeSummary: 'Two LEDs in series',
      difficulty: 'beginner',
      validationStatus: 'theoretical',
      baseCircuit: { slug: 'led-resistor' },
      path: [{ slug: 'led-resistor-basic' }, { slug: 'led-pair' }],
      keyComponents: [{ partNumber: 'LTL-307EE', role: 'LED' }],
      source: { title: 'Ohm Sweet Ohm original design', url: null },
      schematicUrl: '/blocks/led-pair/schematic.svg',
    });
    expect(body.specs).toEqual(
      expect.arrayContaining([
        {
          key: 'supplyVoltage',
          label: expect.any(String) as string,
          kind: 'number',
          quantity: 'voltage',
          unit: 'V',
          min: 5,
          max: 5,
        },
        {
          key: 'ledCount',
          label: expect.any(String) as string,
          kind: 'number',
          quantity: 'count',
          unit: null,
          min: 1,
          max: 1,
        },
        { key: 'ledColor', label: expect.any(String) as string, kind: 'enum', value: 'red' },
      ]),
    );
    expect(body.formulas.length).toBeGreaterThan(0);
  });

  it('should return 404 for an unknown block', async () => {
    const response = await app.inject({ method: 'GET', url: '/blocks/nope' });

    expect(response.statusCode).toBe(404);
    expect(response.json()).toEqual({ error: 'no block "nope"' });
  });

  it('should reject a malformed slug', async () => {
    const response = await app.inject({ method: 'GET', url: '/blocks/Bad_Slug' });

    expect(response.statusCode).toBe(400);
    expect(response.json<{ error: string }>().error).toContain('slug');
  });
});

describe('GET /blocks/:slug/schematic.svg', () => {
  it('should serve the SVG with a hash ETag and headers that forbid running code', async () => {
    const response = await app.inject({
      method: 'GET',
      url: '/blocks/led-resistor-basic/schematic.svg',
    });

    expect(response.statusCode).toBe(200);
    expect(response.body).toBe(SVG);
    expect(response.headers).toMatchObject({
      'content-type': 'image/svg+xml; charset=utf-8',
      etag: '"abc123"',
      'x-content-type-options': 'nosniff',
      'cache-control': 'public, no-cache',
      'content-security-policy': "default-src 'none'; style-src 'unsafe-inline'; sandbox",
    });
  });

  it.each(['"abc123"', '"old", "abc123"', 'W/"abc123"', '*'])(
    'should answer 304 without a body when If-None-Match is %s',
    async (ifNoneMatch) => {
      const response = await app.inject({
        method: 'GET',
        url: '/blocks/led-resistor-basic/schematic.svg',
        headers: { 'if-none-match': ifNoneMatch },
      });

      expect(response.statusCode).toBe(304);
      expect(response.body).toBe('');
    },
  );

  it('should send the SVG again when the ETag is stale', async () => {
    const response = await app.inject({
      method: 'GET',
      url: '/blocks/led-resistor-basic/schematic.svg',
      headers: { 'if-none-match': '"old"' },
    });

    expect(response.statusCode).toBe(200);
  });

  it('should return 404 when the block has no schematic', async () => {
    const response = await app.inject({ method: 'GET', url: '/blocks/led-pair/schematic.svg' });

    expect(response.statusCode).toBe(404);
  });
});

describe('unknown routes', () => {
  it('should answer the documented error shape', async () => {
    const response = await app.inject({ method: 'GET', url: '/nope' });

    expect([response.statusCode, response.json()]).toEqual([404, { error: 'no route GET /nope' }]);
  });
});

describe('server errors', () => {
  it('should answer a generic error without exposing the cause', async () => {
    const failing = await buildApp({
      catalogue: { get: () => Promise.reject(new Error('connect ECONNREFUSED 10.0.0.5:5432')) },
      schematics: { findSchematic: () => Promise.reject(new Error('connect ECONNREFUSED')) },
    });

    const responses = await Promise.all([
      failing.inject({ method: 'GET', url: '/blocks/led-pair' }),
      failing.inject({ method: 'GET', url: '/blocks/led-pair/schematic.svg' }),
    ]);
    await failing.close();

    expect(responses.map((response) => [response.statusCode, response.body])).toEqual([
      [500, '{"error":"internal server error"}'],
      [500, '{"error":"internal server error"}'],
    ]);
  });
});

describe('documentation', () => {
  it('should publish an OpenAPI document listing the block routes', async () => {
    const response = await app.inject({ method: 'GET', url: '/docs/json' });

    expect(Object.keys(response.json<{ paths: object }>().paths)).toEqual([
      '/blocks/{slug}',
      '/blocks/{slug}/schematic.svg',
    ]);
  });
});
