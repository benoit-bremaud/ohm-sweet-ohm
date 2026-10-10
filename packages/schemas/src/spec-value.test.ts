import { describe, expect, it } from 'vitest';

import { parseSpecValue } from './spec-value.js';

const OHM_SIGN = 'Ω';
const GREEK_MU = 'μ';

describe('parseSpecValue', () => {
  describe('single measures', () => {
    it.each([
      ['5 V', 5, 'VOLTAGE'],
      ['3.3V', 3.3, 'VOLTAGE'],
      ['-12 V', -12, 'VOLTAGE'],
      ['13.6 mA', 0.0136, 'CURRENT'],
      ['100 µA (micro sign)', 0.0001, 'CURRENT'],
      [`100 ${GREEK_MU}A (Greek mu)`, 0.0001, 'CURRENT'],
      ['100 uA', 0.0001, 'CURRENT'],
      ['4.7 kΩ (Greek omega)', 4700, 'RESISTANCE'],
      [`4.7 k${OHM_SIGN} (ohm sign)`, 4700, 'RESISTANCE'],
      [`220 ${OHM_SIGN}`, 220, 'RESISTANCE'],
      ['220 ohm', 220, 'RESISTANCE'],
      ['4.7 kohm', 4700, 'RESISTANCE'],
      ['1 mΩ', 0.001, 'RESISTANCE'],
      ['1 MΩ', 1_000_000, 'RESISTANCE'],
      ['1 mHz', 0.001, 'FREQUENCY'],
      ['1.5 MHz', 1_500_000, 'FREQUENCY'],
      ['2 GHz', 2_000_000_000, 'FREQUENCY'],
      ['10 pW', 1e-11, 'POWER'],
      ['5 nA', 5e-9, 'CURRENT'],
      ['41 mW', 0.041, 'POWER'],
    ])('reads "%s" as %d in SI (%s)', (label, value, quantity) => {
      const written = label.replace(/ \(.*\)$/, '');

      const result = parseSpecValue(written);

      expect(result).toEqual({
        ok: true,
        value: { kind: 'measure', min: value, max: value, quantity },
      });
    });

    it('keeps a 14-digit value exactly instead of rounding it', () => {
      expect(parseSpecValue('1.0000000000001 V')).toEqual({
        ok: true,
        value: { kind: 'measure', min: 1.0000000000001, max: 1.0000000000001, quantity: 'VOLTAGE' },
      });
    });

    it('reads a written zero as zero', () => {
      expect(parseSpecValue('0.000 V')).toEqual({
        ok: true,
        value: { kind: 'measure', min: 0, max: 0, quantity: 'VOLTAGE' },
      });
    });

    it('turns a negative zero into zero', () => {
      expect(parseSpecValue('-0 V')).toEqual({
        ok: true,
        value: { kind: 'measure', min: 0, max: 0, quantity: 'VOLTAGE' },
      });
    });

    it.each([
      ['5 mAh', 'unknown unit "mAh"'],
      ['5 kV/s', 'unknown unit "kV/s"'],
      ['5 m', 'unknown unit "m"'],
      ['5 volts', 'unknown unit "volts"'],
      ['1.0', '"1.0" has no unit'],
      ['1e3 V', '"1e3 V" is not a valid number with a unit'],
      ['5,5 V', '"5,5 V" is not a valid number with a unit'],
      ['5. V', '"5. V" is not a valid number with a unit'],
      ['.5 V', '".5 V" is not a valid number with a unit'],
      ['0x10', '"0x10" is not a valid number with a unit'],
      [`${'9'.repeat(400)} GV`, 'has more than 15 significant digits'],
      ['1.000000000000001 V', 'has more than 15 significant digits'],
      [`0.${'0'.repeat(400)}1 pA`, 'is out of range'],
      [`0.${'0'.repeat(309)}1 V`, 'is out of range'],
    ])('rejects "%s"', (written, message) => {
      const result = parseSpecValue(written);

      expect(result).toEqual({ ok: false, error: expect.stringContaining(message) as unknown });
    });
  });

  describe('ranges', () => {
    it.each([
      ['7 V .. 15 V', 7, 15, 'VOLTAGE'],
      ['7V..15V', 7, 15, 'VOLTAGE'],
      ['500 mA .. 1.5 A', 0.5, 1.5, 'CURRENT'],
      ['-15 V .. -7 V', -15, -7, 'VOLTAGE'],
      ['5 V .. 5 V', 5, 5, 'VOLTAGE'],
    ])('reads "%s" as [%d, %d] in SI', (written, min, max, quantity) => {
      expect(parseSpecValue(written)).toEqual({
        ok: true,
        value: { kind: 'measure', min, max, quantity },
      });
    });

    it.each([
      ['15 V .. 7 V', 'range start is greater than its end'],
      ['1.000000000001 V .. 1 V', 'range start is greater than its end'],
      ['7 V .. 1 A', 'range ends mix VOLTAGE and CURRENT'],
      ['7 .. 15 V', 'range start: "7" has no unit'],
      ['7 V .. 15', 'range end: "15" has no unit'],
      ['7 V .. 9 V .. 15 V', 'must have exactly one ".."'],
      ['7 V ... 15 V', 'the range separator is exactly ".."'],
    ])('rejects "%s"', (written, message) => {
      expect(parseSpecValue(written)).toEqual({
        ok: false,
        error: expect.stringContaining(message) as unknown,
      });
    });
  });

  describe('counts', () => {
    it.each([
      ['1', 1],
      ['12', 12],
      ['-0', 0],
    ])('reads "%s" as the count %d', (written, value) => {
      expect(parseSpecValue(written)).toEqual({ ok: true, value: { kind: 'count', value } });
    });

    it('rejects an integer too large to be represented exactly', () => {
      expect(parseSpecValue('12345678901234567891')).toEqual({
        ok: false,
        error: '"12345678901234567891" is out of range',
      });
    });
  });

  describe('enum words', () => {
    it.each(['red', 'low-pass', 'n-mosfet'])('reads "%s" as an enum word', (word) => {
      expect(parseSpecValue(word)).toEqual({ ok: true, value: { kind: 'text', text: word } });
    });

    it.each(['red-', 'red--blue', '-red', 'Red', 'Red LED', 'low_pass'])(
      'rejects the malformed word "%s" with a word-specific message',
      (written) => {
        expect(parseSpecValue(written)).toEqual({
          ok: false,
          error: `"${written}" must be a lowercase kebab-case word, e.g. low-pass`,
        });
      },
    );

    it('reads a bare unit name as a word, leaving the type check to the domain', () => {
      expect(parseSpecValue('ohm')).toEqual({ ok: true, value: { kind: 'text', text: 'ohm' } });
    });
  });
});
