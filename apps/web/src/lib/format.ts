import type { BlockResponse } from '@ohm-sweet-ohm/schemas';

type Spec = BlockResponse['specs'][number];

/** SI prefixes a maker reads on a datasheet; chosen so the mantissa falls in [1, 1000). */
const NANO = [-9, 'n'] as const;
const PREFIXES: readonly (readonly [exponent: number, symbol: string])[] = [
  [9, 'G'],
  [6, 'M'],
  [3, 'k'],
  [0, ''],
  [-3, 'm'],
  [-6, 'µ'],
  NANO,
];

const number = new Intl.NumberFormat('en', { maximumSignificantDigits: 3 });

/** 0.0136 A → "13.6 mA"; 5 V → "5 V"; a count has no unit → "1". */
export function formatQuantity(value: number, unit: string | null): string {
  if (unit === null) {
    return number.format(value);
  }
  if (value === 0) {
    return `0\u00a0${unit}`;
  }
  const magnitude = Math.floor(Math.log10(Math.abs(value)));
  const [exponent, symbol] = PREFIXES.find(([candidate]) => magnitude >= candidate) ?? NANO;
  // Non-breaking space: a value never separates from its unit at a line end.
  return `${number.format(value / 10 ** exponent)}\u00a0${symbol}${unit}`;
}

/** A single value, or "min to max" for a range. */
export function formatSpec(spec: Spec): string {
  if (spec.kind === 'enum') {
    return spec.value;
  }
  const min = formatQuantity(spec.min, spec.unit);
  return spec.min === spec.max ? min : `${min} to ${formatQuantity(spec.max, spec.unit)}`;
}

/** First letter up, the rest untouched: API values are lowercase by contract. */
export function sentence(value: string): string {
  return value.charAt(0).toUpperCase() + value.slice(1);
}
