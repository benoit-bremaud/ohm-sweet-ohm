import { describe, expect, it, vi } from 'vitest';

import { blockResponseSchema } from '@ohm-sweet-ohm/schemas';

import { type CatalogueReader, findBlock, isSlug } from './catalogue';
import { makeCatalogue } from './test-catalogue';

function reading(catalogue = makeCatalogue()): CatalogueReader {
  return {
    catalogue: vi.fn(() => Promise.resolve(catalogue)),
    findSchematic: vi.fn(() => Promise.resolve(undefined)),
  };
}

describe('isSlug', () => {
  it.each(['led-resistor-basic', 'a', 'v2'])('accepts %s', (slug) => {
    expect(isSlug(slug)).toBe(true);
  });

  it.each(['', 'Bad_Slug', '-led', 'led-', 'a/b', '../etc'])('rejects %j', (slug) => {
    expect(isSlug(slug)).toBe(false);
  });
});

describe('findBlock', () => {
  it('returns a variant with lowercase values, SI units and its path', async () => {
    const lookup = await findBlock(reading(), 'led-pair');

    expect(lookup.kind).toBe('found');
    const block = blockResponseSchema.parse(lookup.kind === 'found' ? lookup.block : undefined);
    expect(block).toMatchObject({
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
    expect(block.specs).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ key: 'supplyVoltage', quantity: 'voltage', unit: 'V', min: 5 }),
        expect.objectContaining({ key: 'ledCount', quantity: 'count', unit: null }),
        expect.objectContaining({ key: 'ledColor', kind: 'enum', value: 'red' }),
      ]),
    );
    expect(block.formulas.length).toBeGreaterThan(0);
  });

  it('never reads the database for a malformed slug', async () => {
    const catalogue = vi.fn(() => Promise.resolve(makeCatalogue()));

    const lookup = await findBlock({ ...reading(), catalogue }, '../admin');

    expect(lookup).toEqual({ kind: 'not-found' });
    expect(catalogue).not.toHaveBeenCalled();
  });

  it('reports an unknown block as not found', async () => {
    expect(await findBlock(reading(), 'nope')).toEqual({ kind: 'not-found' });
  });

  it('reports a database failure as unavailable, with the cause for the logs', async () => {
    const reader: CatalogueReader = {
      catalogue: () => Promise.reject(new Error('ECONNREFUSED')),
      findSchematic: () => Promise.resolve(undefined),
    };

    const lookup = await findBlock(reader, 'led-resistor-basic');

    expect(lookup).toEqual({ kind: 'unavailable', reason: 'catalogue unreachable: ECONNREFUSED' });
  });

  it('reports a non-Error rejection as unavailable too', async () => {
    const reader: CatalogueReader = {
      // eslint-disable-next-line @typescript-eslint/prefer-promise-reject-errors -- the case under test
      catalogue: () => Promise.reject('timeout'),
      findSchematic: () => Promise.resolve(undefined),
    };

    expect(await findBlock(reader, 'led')).toEqual({
      kind: 'unavailable',
      reason: 'catalogue unreachable: timeout',
    });
  });

  it('refuses a block whose source link is not http(s), so no javascript: href reaches the page', async () => {
    const catalogue = makeCatalogue();
    const block = catalogue.findBlock('led-resistor-basic');
    if (block === undefined) throw new Error('fixture changed');
    // Simulates a row that slipped past the importer's validation.
    Object.assign(block.source, { url: 'javascript:alert(1)' });

    const lookup = await findBlock(reading(catalogue), 'led-resistor-basic');

    expect(lookup).toMatchObject({
      kind: 'unavailable',
      reason: expect.stringContaining('off contract') as string,
    });
  });
});
