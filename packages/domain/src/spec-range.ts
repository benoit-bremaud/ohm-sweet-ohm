/** A closed interval in SI units; a single value is a range whose ends are equal. */
export class SpecRange {
  readonly min: number;
  readonly max: number;

  constructor(min: number, max: number) {
    if (!Number.isFinite(min) || !Number.isFinite(max) || min > max) {
      throw new RangeError(`invalid range [${String(min)}, ${String(max)}]`);
    }
    this.min = min;
    this.max = max;
  }

  contains(other: SpecRange): boolean {
    return this.min <= other.min && other.max <= this.max;
  }

  equals(other: SpecRange): boolean {
    return this.min === other.min && this.max === other.max;
  }
}
