/**
 * Reads the spec value notation of `meta.yaml` (docs/architecture/specs/catalogue-format.md)
 * and converts it to SI numbers. This is boundary code: it checks notation only. Whether a key
 * expects a measure, a count or an enum value is a domain rule.
 */

export const QUANTITIES = ['VOLTAGE', 'CURRENT', 'RESISTANCE', 'FREQUENCY', 'POWER'] as const;
export type Quantity = (typeof QUANTITIES)[number];

/** A spec value as written by the curator, converted to SI. Mirrors `RawSpec` in the class diagram. */
export type RawSpecValue =
  | {
      readonly kind: 'measure';
      readonly min: number;
      readonly max: number;
      readonly quantity: Quantity;
    }
  | { readonly kind: 'count'; readonly value: number }
  | { readonly kind: 'text'; readonly text: string };

export type SpecValueResult =
  | { readonly ok: true; readonly value: RawSpecValue }
  | { readonly ok: false; readonly error: string };

const UNITS: Readonly<Record<string, Quantity>> = {
  V: 'VOLTAGE',
  A: 'CURRENT',
  '\u03a9': 'RESISTANCE', // GREEK CAPITAL LETTER OMEGA, the usual ohm symbol
  '\u2126': 'RESISTANCE', // OHM SIGN, a look-alike of the Greek capital omega
  ohm: 'RESISTANCE',
  Hz: 'FREQUENCY',
  W: 'POWER',
};

const PREFIXES: Readonly<Record<string, number>> = {
  p: 1e-12,
  n: 1e-9,
  '\u00b5': 1e-6, // MICRO SIGN
  '\u03bc': 1e-6, // GREEK SMALL LETTER MU, a look-alike of the micro sign
  u: 1e-6,
  m: 1e-3,
  k: 1e3,
  M: 1e6,
  G: 1e9,
};

const NUMBER = String.raw`[+-]?\d+(?:\.\d+)?`;
/**
 * A number, then optionally a unit that cannot start like the rest of a number: `.` `,` (decimals),
 * `e` (exponent), `x` (hexadecimal).
 */
const MEASURE = new RegExp(String.raw`^(${NUMBER})(?:\s*([^\d.,eExX\s].*))?$`);
const INTEGER = /^[+-]?\d+$/;
const ENUM_WORD = /^[a-z][a-z0-9-]*$/;
const RANGE_SEPARATOR = '..';

/** Significant digits kept after SI conversion, so `4.7 kΩ` becomes exactly 4700. */
const SIGNIFICANT_DIGITS = 12;

interface Measure {
  readonly value: number;
  readonly quantity: Quantity;
}
type MeasureResult =
  { readonly ok: true; readonly measure: Measure } | { readonly ok: false; readonly error: string };

function parseUnit(
  symbol: string,
): { readonly factor: number; readonly quantity: Quantity } | undefined {
  const bare = UNITS[symbol];
  if (bare !== undefined) {
    return { factor: 1, quantity: bare };
  }
  const prefix = PREFIXES[symbol.charAt(0)];
  const unit = UNITS[symbol.slice(1)];
  if (prefix === undefined || unit === undefined) {
    return undefined;
  }
  return { factor: prefix, quantity: unit };
}

/** Converts to SI, keeps 12 significant digits and turns -0 into 0. */
function toSi(number: string, factor: number): number {
  return Number((Number(number) * factor).toPrecision(SIGNIFICANT_DIGITS)) + 0;
}

function parseMeasure(text: string): MeasureResult {
  const match = MEASURE.exec(text);
  if (match === null) {
    return { ok: false, error: `"${text}" is not a valid number with a unit` };
  }
  const [, number = '', symbol] = match;
  if (symbol === undefined) {
    return { ok: false, error: `"${text}" has no unit` };
  }
  const unit = parseUnit(symbol);
  if (unit === undefined) {
    return { ok: false, error: `unknown unit "${symbol}"` };
  }
  const value = toSi(number, unit.factor);
  if (!Number.isFinite(value)) {
    return { ok: false, error: `"${text}" is out of range` };
  }
  return { ok: true, measure: { value, quantity: unit.quantity } };
}

function parseRange(text: string): SpecValueResult {
  if (text.includes('...')) {
    return { ok: false, error: `the range separator is exactly "${RANGE_SEPARATOR}" in "${text}"` };
  }
  const parts = text.split(RANGE_SEPARATOR);
  const [lowText, highText] = parts;
  if (parts.length !== 2 || lowText === undefined || highText === undefined) {
    return { ok: false, error: `"${text}" must have exactly one "${RANGE_SEPARATOR}"` };
  }
  const low = parseMeasure(lowText.trim());
  if (!low.ok) {
    return { ok: false, error: `range start: ${low.error}` };
  }
  const high = parseMeasure(highText.trim());
  if (!high.ok) {
    return { ok: false, error: `range end: ${high.error}` };
  }
  if (low.measure.quantity !== high.measure.quantity) {
    return {
      ok: false,
      error: `range ends mix ${low.measure.quantity} and ${high.measure.quantity}`,
    };
  }
  if (low.measure.value > high.measure.value) {
    return { ok: false, error: `range start is greater than its end in "${text}"` };
  }
  return {
    ok: true,
    value: {
      kind: 'measure',
      min: low.measure.value,
      max: high.measure.value,
      quantity: low.measure.quantity,
    },
  };
}

/**
 * Parses one spec value exactly as written in `meta.yaml`: a measure, a range, an integer count
 * or a lowercase enum word. A single measure is returned as a range with `min === max`.
 */
export function parseSpecValue(written: string): SpecValueResult {
  const text = written.trim();
  if (text.includes(RANGE_SEPARATOR)) {
    return parseRange(text);
  }
  if (INTEGER.test(text)) {
    const count = Number(text) + 0;
    return Number.isSafeInteger(count)
      ? { ok: true, value: { kind: 'count', value: count } }
      : { ok: false, error: `"${text}" is out of range` };
  }
  if (ENUM_WORD.test(text)) {
    return { ok: true, value: { kind: 'text', text } };
  }
  const single = parseMeasure(text);
  return single.ok
    ? {
        ok: true,
        value: {
          kind: 'measure',
          min: single.measure.value,
          max: single.measure.value,
          quantity: single.measure.quantity,
        },
      }
    : single;
}
