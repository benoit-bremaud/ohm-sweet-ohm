import { describe, expect, it } from 'vitest';

import { SpecRange } from './spec-range.js';
import {
  EnumParameterDefinition,
  EnumSpec,
  NumericParameterDefinition,
  NumericSpec,
} from './specs.js';
import { ValidationError } from './validation-error.js';

const voltage = new NumericParameterDefinition(
  'supplyVoltage',
  'Supply voltage',
  true,
  'VOLTAGE',
  'COVERS',
);
const count = new NumericParameterDefinition('ledCount', 'Number of LEDs', true, 'COUNT', 'WITHIN');
const color = new EnumParameterDefinition('ledColor', 'LED colour', true, ['red', 'green']);

describe('SpecRange', () => {
  it('rejects a reversed range', () => {
    expect(() => new SpecRange(2, 1)).toThrow(RangeError);
  });

  it('contains a range inside it, ends included', () => {
    expect(new SpecRange(7, 15).contains(new SpecRange(7, 12))).toBe(true);
    expect(new SpecRange(7, 15).contains(new SpecRange(5, 12))).toBe(false);
  });
});

describe('NumericParameterDefinition.createSpec', () => {
  it('creates a spec from a measure of its quantity', () => {
    const spec = voltage.createSpec({ key: 'supplyVoltage', min: 7, max: 15, quantity: 'VOLTAGE' });

    expect(spec).toBeInstanceOf(NumericSpec);
    expect(spec instanceof NumericSpec && [spec.range.min, spec.range.max]).toEqual([7, 15]);
  });

  it.each([
    [
      { key: 'supplyVoltage', min: 0.02, max: 0.02, quantity: 'CURRENT' as const },
      'expects a voltage, got a current',
    ],
    [{ key: 'supplyVoltage', min: 5, max: 5 }, 'expects a voltage, got a number without unit'],
    [{ key: 'supplyVoltage', text: 'red' }, 'expects a voltage value, not the word "red"'],
  ])('rejects %o', (raw, message) => {
    expect(voltage.createSpec(raw)).toEqual(new ValidationError('specs.supplyVoltage', message));
  });

  it.each([
    [
      { key: 'supplyVoltage', min: Number.NaN, max: 5, quantity: 'VOLTAGE' as const },
      'expects a finite number',
    ],
    [
      { key: 'supplyVoltage', min: 1, max: Number.POSITIVE_INFINITY, quantity: 'VOLTAGE' as const },
      'expects a finite number',
    ],
    [
      { key: 'supplyVoltage', min: 5, quantity: 'VOLTAGE' as const },
      'expects both ends of the range',
    ],
    [
      { key: 'supplyVoltage', min: 15, max: 7, quantity: 'VOLTAGE' as const },
      'range start is greater than its end',
    ],
  ])('returns an error, never throws, for %o', (raw, message) => {
    expect(voltage.createSpec(raw)).toEqual(new ValidationError('specs.supplyVoltage', message));
  });

  it('accepts a positive integer count without unit', () => {
    expect(count.createSpec({ key: 'ledCount', min: 2, max: 2 })).toBeInstanceOf(NumericSpec);
  });

  it.each([
    [{ key: 'ledCount', min: 0, max: 0 }, 'expects a positive integer count'],
    [{ key: 'ledCount', min: 1.5, max: 1.5 }, 'expects a positive integer count'],
    [
      { key: 'ledCount', min: 2, max: 2, quantity: 'VOLTAGE' as const },
      'expects a count without unit, got a voltage',
    ],
  ])('rejects the count %o', (raw, message) => {
    expect(count.createSpec(raw)).toEqual(new ValidationError('specs.ledCount', message));
  });
});

describe('EnumParameterDefinition.createSpec', () => {
  it('creates a spec from an allowed value', () => {
    expect(color.createSpec({ key: 'ledColor', text: 'red' })).toBeInstanceOf(EnumSpec);
  });

  it('rejects a value outside the allowed values', () => {
    expect(color.createSpec({ key: 'ledColor', text: 'blue' })).toEqual(
      new ValidationError('specs.ledColor', '"blue" is not one of red, green'),
    );
  });

  it('rejects a number', () => {
    expect(color.createSpec({ key: 'ledColor', min: 1, max: 1 })).toEqual(
      new ValidationError('specs.ledColor', 'expects one of red, green, got a number'),
    );
  });

  it('refuses a definition listing an allowed value twice', () => {
    expect(() => new EnumParameterDefinition('ledColor', 'Colour', true, ['red', 'red'])).toThrow(
      /twice/,
    );
  });

  it('refuses a definition without allowed values', () => {
    expect(() => new EnumParameterDefinition('ledColor', 'LED colour', true, [])).toThrow(
      RangeError,
    );
  });
});

describe('Spec.toRaw', () => {
  it.each([
    [voltage, { key: 'supplyVoltage', min: 7, max: 15, quantity: 'VOLTAGE' as const }],
    [count, { key: 'ledCount', min: 2, max: 2 }],
    [color, { key: 'ledColor', text: 'red' }],
  ])('gives back the raw value the spec was created from (%#)', (definition, raw) => {
    const spec = definition.createSpec(raw);

    expect(spec instanceof ValidationError ? spec : spec.toRaw()).toEqual(raw);
  });
});

describe('sameKindAs', () => {
  it('matches numeric definitions only with the same quantity and match mode', () => {
    const same = new NumericParameterDefinition('supplyVoltage', 'Vin', false, 'VOLTAGE', 'COVERS');
    const otherMode = new NumericParameterDefinition(
      'supplyVoltage',
      'Vin',
      false,
      'VOLTAGE',
      'WITHIN',
    );

    expect([
      voltage.sameKindAs(same),
      voltage.sameKindAs(otherMode),
      voltage.sameKindAs(color),
    ]).toEqual([true, false, false]);
  });

  it('matches enum definitions only with the same allowed values', () => {
    const reordered = new EnumParameterDefinition('ledColor', 'Colour', false, ['green', 'red']);
    const wider = new EnumParameterDefinition('ledColor', 'Colour', false, [
      'red',
      'green',
      'blue',
    ]);

    expect([color.sameKindAs(reordered), color.sameKindAs(wider)]).toEqual([true, false]);
  });
});
