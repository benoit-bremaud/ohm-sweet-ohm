import { SpecRange } from './spec-range.js';
import { ValidationError } from './validation-error.js';
import type { MatchMode, Quantity } from './vocabulary.js';

/**
 * A spec value as read from the catalogue, before it is typed by its definition. Mirrors `RawSpec`
 * in 04-class.md: a measure has `min`, `max` and `quantity`; a count has `min` and `max` only; an
 * enum value has `text` only.
 */
export interface RawSpec {
  readonly key: string;
  readonly min?: number;
  readonly max?: number;
  readonly quantity?: Exclude<Quantity, 'COUNT'>;
  readonly text?: string;
}

/** A typed value of one parameter of a block. */
export abstract class Spec {
  protected constructor(readonly definition: ParameterDefinition) {}

  get key(): string {
    return this.definition.key;
  }

  /** The raw value this spec was created from; `definition.createSpec(spec.toRaw())` rebuilds it. */
  abstract toRaw(): RawSpec;
}

export class NumericSpec extends Spec {
  constructor(
    override readonly definition: NumericParameterDefinition,
    readonly range: SpecRange,
  ) {
    super(definition);
  }

  toRaw(): RawSpec {
    const { quantity } = this.definition;
    return {
      key: this.key,
      min: this.range.min,
      max: this.range.max,
      ...(quantity === 'COUNT' ? {} : { quantity }),
    };
  }
}

export class EnumSpec extends Spec {
  constructor(
    override readonly definition: EnumParameterDefinition,
    readonly value: string,
  ) {
    super(definition);
  }

  toRaw(): RawSpec {
    return { key: this.key, text: this.value };
  }
}

/** The type of one parameter of a base circuit; turns a raw value into a typed spec. */
export abstract class ParameterDefinition {
  protected constructor(
    readonly key: string,
    readonly label: string,
    readonly required: boolean,
  ) {}

  /** Returns the typed spec, or the error explaining why the raw value does not fit. */
  abstract createSpec(raw: RawSpec): Spec | ValidationError;

  /** True when both definitions give the key the same meaning (shared-key invariant). */
  abstract sameKindAs(other: ParameterDefinition): boolean;

  protected error(message: string): ValidationError {
    return new ValidationError(`specs.${this.key}`, message);
  }
}

export class NumericParameterDefinition extends ParameterDefinition {
  constructor(
    key: string,
    label: string,
    required: boolean,
    readonly quantity: Quantity,
    readonly matchMode: MatchMode,
  ) {
    super(key, label, required);
  }

  createSpec(raw: RawSpec): NumericSpec | ValidationError {
    if (raw.min === undefined || raw.max === undefined) {
      return this.error(
        raw.text === undefined
          ? 'expects both ends of the range'
          : `expects a ${this.quantity.toLowerCase()} value, not the word "${raw.text}"`,
      );
    }
    if (!Number.isFinite(raw.min) || !Number.isFinite(raw.max)) {
      return this.error('expects a finite number');
    }
    if (this.quantity === 'COUNT') {
      if (raw.quantity !== undefined) {
        return this.error(`expects a count without unit, got a ${raw.quantity.toLowerCase()}`);
      }
      if (!Number.isInteger(raw.min) || !Number.isInteger(raw.max) || raw.min < 1) {
        return this.error('expects a positive integer count');
      }
    } else if (raw.quantity !== this.quantity) {
      const got =
        raw.quantity === undefined ? 'a number without unit' : `a ${raw.quantity.toLowerCase()}`;
      return this.error(`expects a ${this.quantity.toLowerCase()}, got ${got}`);
    }
    if (raw.min > raw.max) {
      return this.error('range start is greater than its end');
    }
    return new NumericSpec(this, new SpecRange(raw.min, raw.max));
  }

  sameKindAs(other: ParameterDefinition): boolean {
    return (
      other instanceof NumericParameterDefinition &&
      other.quantity === this.quantity &&
      other.matchMode === this.matchMode
    );
  }
}

export class EnumParameterDefinition extends ParameterDefinition {
  readonly allowedValues: readonly string[];

  constructor(key: string, label: string, required: boolean, allowedValues: readonly string[]) {
    super(key, label, required);
    if (allowedValues.length === 0) {
      throw new RangeError(`enum parameter ${key} needs at least one allowed value`);
    }
    if (new Set(allowedValues).size !== allowedValues.length) {
      throw new RangeError(`enum parameter ${key} lists an allowed value twice`);
    }
    this.allowedValues = allowedValues;
  }

  createSpec(raw: RawSpec): EnumSpec | ValidationError {
    if (raw.text === undefined) {
      return this.error(`expects one of ${this.allowedValues.join(', ')}, got a number`);
    }
    if (!this.allowedValues.includes(raw.text)) {
      return this.error(`"${raw.text}" is not one of ${this.allowedValues.join(', ')}`);
    }
    return new EnumSpec(this, raw.text);
  }

  sameKindAs(other: ParameterDefinition): boolean {
    return (
      other instanceof EnumParameterDefinition &&
      other.allowedValues.length === this.allowedValues.length &&
      other.allowedValues.every((value) => this.allowedValues.includes(value))
    );
  }
}
