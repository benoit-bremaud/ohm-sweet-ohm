import type { BlockResponse } from '@ohm-sweet-ohm/schemas';

type Spec = BlockResponse['specs'][number];

/**
 * SI prefixes a maker reads on a datasheet, chosen so the mantissa falls in [1, 1000) between
 * nano and giga; outside that range the nearest prefix is kept.
 */
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

const threeDigits = new Intl.NumberFormat('en', {
  maximumSignificantDigits: 3,
  useGrouping: false,
});

/**
 * Three significant digits, an SI prefix and a non-breaking space before the unit:
 * 0.0136 A → "13.6 mA"; 5 V → "5 V"; a count has no unit → "1".
 */
export function formatQuantity(value: number, unit: string | null): string {
  if (unit === null) {
    return threeDigits.format(value);
  }
  if (value === 0) {
    return `0\u00a0${unit}`;
  }
  // Round before choosing the prefix, so 0.9996 A reads "1 A", not "1000 mA".
  const magnitude = Math.floor(Math.log10(Number(Math.abs(value).toPrecision(3))));
  const [exponent, symbol] = PREFIXES.find(([candidate]) => magnitude >= candidate) ?? NANO;
  return `${threeDigits.format(value / 10 ** exponent)}\u00a0${symbol}${unit}`;
}

/** A single value, or "min to max" for a range; an enumerated value in sentence case. */
export function formatSpec(spec: Spec): string {
  if (spec.kind === 'enum') {
    return sentence(spec.value);
  }
  const min = formatQuantity(spec.min, spec.unit);
  return spec.min === spec.max ? min : `${min} to ${formatQuantity(spec.max, spec.unit)}`;
}

/** First letter up, the rest untouched: API values are lowercase by contract. */
export function sentence(value: string): string {
  return value.charAt(0).toUpperCase() + value.slice(1);
}
