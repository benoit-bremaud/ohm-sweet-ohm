import { readFile } from 'node:fs/promises';

import { describe, expect, it } from 'vitest';

import { readBlockMeta, type ReadError } from './block-meta.js';

const LED_META = new URL(
  '../../../catalogue/led-resistor/led-resistor-basic/meta.yaml',
  import.meta.url,
);

const VALID = `
slug: test-block
name: Test block
description: A block used by the tests.
baseCircuit: led-resistor
difficulty: beginner
validationStatus: theoretical
hazardous: false
specs:
  supplyVoltage: 7 V .. 15 V
  ledColor: red
source:
  title: Test source
`;

function fieldsOf(yaml: string): readonly string[] {
  const result = readBlockMeta(yaml);
  return result.ok ? [] : result.errors.map((error) => error.field);
}

function errorsOf(yaml: string): readonly ReadError[] {
  const result = readBlockMeta(yaml);
  return result.ok ? [] : result.errors;
}

describe('readBlockMeta', () => {
  it('reads the LED block of the catalogue', async () => {
    const yaml = await readFile(LED_META, 'utf8');

    const result = readBlockMeta(yaml);

    expect(result).toEqual({
      ok: true,
      meta: expect.objectContaining({
        slug: 'led-resistor-basic',
        baseCircuit: 'led-resistor',
        keyComponents: [],
        specs: [
          { key: 'supplyVoltage', value: { kind: 'measure', min: 5, max: 5, quantity: 'VOLTAGE' } },
          {
            key: 'ledCurrent',
            value: { kind: 'measure', min: 0.0136, max: 0.0136, quantity: 'CURRENT' },
          },
          { key: 'ledColor', value: { kind: 'text', text: 'red' } },
          { key: 'ledCount', value: { kind: 'count', value: 1 } },
          {
            key: 'resistorPower',
            value: { kind: 'measure', min: 0.041, max: 0.041, quantity: 'POWER' },
          },
        ],
      }) as unknown,
    });
  });

  it('leaves parent and change summary undefined for a root block', () => {
    const result = readBlockMeta(VALID);

    expect(result.ok && [result.meta.parent, result.meta.changeSummary]).toEqual([
      undefined,
      undefined,
    ]);
  });

  it('rejects an unknown field so a typo never goes unnoticed', () => {
    expect(errorsOf(`${VALID}difficult: beginner\n`)).toEqual([
      { field: '', message: expect.stringContaining('difficult') as unknown },
    ]);
  });

  it('reports every shape error with its field path', () => {
    const yaml = VALID.replace('difficulty: beginner', 'difficulty: expert').replace(
      'slug: test-block',
      'slug: Test_Block',
    );

    expect(fieldsOf(yaml)).toEqual(['slug', 'difficulty']);
  });

  it('reports every invalid spec value, not only the first', () => {
    const yaml = VALID.replace('ledColor: red', 'ledColor: Red LED\n  ledCurrent: 5 mAh');

    expect(fieldsOf(yaml)).toEqual(['specs.ledColor', 'specs.ledCurrent']);
  });

  it('reports spec value errors together with shape errors', () => {
    const yaml = VALID.replace('difficulty: beginner', 'difficulty: expert').replace(
      'ledColor: red',
      'ledColor: red\n  ledCurrent: 5 mAh',
    );

    expect(fieldsOf(yaml)).toEqual(['difficulty', 'specs.ledCurrent']);
  });

  it.each([
    ['1e3', '"1e3" is not a valid number with a unit'],
    ['1.0', '"1.0" has no unit'],
    ['0x10', '"0x10" is not a valid number with a unit'],
  ])('checks "%s" as written, before YAML could turn it into a number', (written, message) => {
    const yaml = VALID.replace('ledColor: red', `ledCount: ${written}`);

    expect(errorsOf(yaml)).toEqual([{ field: 'specs.ledCount', message }]);
  });

  it('rejects a spec value that is not a scalar', () => {
    const yaml = VALID.replace('ledColor: red', 'ledColor: [red, green]');

    expect(errorsOf(yaml)).toEqual([
      {
        field: 'specs.ledColor',
        message: 'must be a value with a unit, an integer or a lowercase word',
      },
    ]);
  });

  it('reports a bad key, a bad value and a non-scalar value of the same file together', () => {
    const yaml = VALID.replace(
      'ledColor: red',
      'bad_key: 5 V\n  ledCurrent: 5 mAh\n  ledColor: [red, green]',
    );

    expect(errorsOf(yaml)).toEqual([
      { field: 'specs.bad_key', message: 'key must be camelCase' },
      { field: 'specs.ledCurrent', message: 'unknown unit "mAh"' },
      {
        field: 'specs.ledColor',
        message: 'must be a value with a unit, an integer or a lowercase word',
      },
    ]);
  });

  it('reports a specs field left empty', () => {
    const yaml = VALID.replace(/specs:\n(?: {2}.*\n)+/, 'specs:\n');

    expect(fieldsOf(yaml)).toEqual(['specs']);
  });

  it('requires at least one spec', () => {
    const yaml = VALID.replace(/specs:\n(?: {2}.*\n)+/, 'specs: {}\n');

    expect(errorsOf(yaml)).toEqual([{ field: 'specs', message: 'must declare at least one spec' }]);
  });

  it('accepts only http(s) source URLs', () => {
    const yaml = VALID.replace(
      'title: Test source',
      'title: Test source\n  url: ftp://example.com/x',
    );

    expect(fieldsOf(yaml)).toEqual(['source.url']);
  });

  it('rejects a duplicate key instead of keeping the last value', () => {
    expect(errorsOf(`${VALID}hazardous: true\n`)).toEqual([
      { field: '', message: expect.stringMatching(/^invalid YAML: .*unique/) as unknown },
    ]);
  });

  it('rejects malformed YAML', () => {
    expect(errorsOf('slug: [unclosed')).toEqual([
      { field: '', message: expect.stringMatching(/^invalid YAML: /) as unknown },
    ]);
  });
});
