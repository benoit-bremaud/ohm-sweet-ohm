import { describe, expect, it } from 'vitest';

import { formatQuantity, formatSpec, sentence } from './format';

const NBSP = ' ';

describe('formatQuantity', () => {
  it.each([
    [5, 'V', `5${NBSP}V`],
    [0.0136, 'A', `13.6${NBSP}mA`],
    [0.041, 'W', `41${NBSP}mW`],
    [220, 'Ω', `220${NBSP}Ω`],
    [4700, 'Ω', `4.7${NBSP}kΩ`],
    [1_000_000, 'Hz', `1${NBSP}MHz`],
    [2.2e-6, 'A', `2.2${NBSP}µA`],
    [1e-12, 'A', `0.001${NBSP}nA`],
    [0, 'V', `0${NBSP}V`],
    [1, null, '1'],
    [12, null, '12'],
  ])('%s %s → %s', (value, unit, expected) => {
    expect(formatQuantity(value, unit)).toBe(expected);
  });

  it('keeps three significant digits', () => {
    expect(formatQuantity(0.013_666, 'A')).toBe(`13.7${NBSP}mA`);
  });
});

describe('formatSpec', () => {
  const numeric = {
    key: 'v',
    label: 'Supply voltage',
    kind: 'number',
    quantity: 'voltage',
    unit: 'V',
  } as const;

  it('shows a single value once', () => {
    expect(formatSpec({ ...numeric, min: 5, max: 5 })).toBe(`5${NBSP}V`);
  });

  it('shows a range as "min to max"', () => {
    expect(formatSpec({ ...numeric, min: 5, max: 12 })).toBe(`5${NBSP}V to 12${NBSP}V`);
  });

  it('passes an enumerated value through', () => {
    expect(formatSpec({ key: 'c', label: 'Colour', kind: 'enum', value: 'red' })).toBe('red');
  });
});

describe('sentence', () => {
  it('capitalises the first letter only', () => {
    expect(sentence('beginner')).toBe('Beginner');
    expect(sentence('')).toBe('');
  });
});
