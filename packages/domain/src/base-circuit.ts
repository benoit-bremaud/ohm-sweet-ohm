import type { ParameterDefinition, RawSpec, Spec } from './specs.js';
import { ValidationError } from './validation-error.js';

/** A design formula of a base circuit, shown on block pages and evaluated by the M4 calculator. */
export class Formula {
  constructor(
    readonly name: string,
    readonly expression: string,
    readonly description: string,
  ) {}
}

/** Outcome of typing raw specs: the specs, or the first validation error. */
export type SpecsResult =
  | { readonly ok: true; readonly specs: readonly Spec[] }
  | { readonly ok: false; readonly errors: readonly ValidationError[] };

/** A well-known circuit whose blocks share the same typed parameters. */
export class BaseCircuit {
  private readonly parameters: ReadonlyMap<string, ParameterDefinition>;

  constructor(
    readonly slug: string,
    readonly name: string,
    /** Position in the learning progression, from the simplest circuit. */
    readonly order: number,
    parameters: readonly ParameterDefinition[],
    readonly formulas: readonly Formula[] = [],
  ) {
    if (parameters.length === 0) {
      throw new RangeError(`base circuit ${slug} needs at least one parameter`);
    }
    const byKey = new Map<string, ParameterDefinition>();
    for (const parameter of parameters) {
      if (byKey.has(parameter.key)) {
        throw new RangeError(`base circuit ${slug} defines ${parameter.key} twice`);
      }
      byKey.set(parameter.key, parameter);
    }
    this.parameters = byKey;
  }

  get parameterDefinitions(): readonly ParameterDefinition[] {
    return [...this.parameters.values()];
  }

  definitionOf(key: string): ParameterDefinition | undefined {
    return this.parameters.get(key);
  }

  /**
   * Types raw specs against this base circuit's definitions and reports every problem: unknown or
   * duplicate key, missing required key, value rejected by its definition.
   */
  specsFrom(raw: readonly RawSpec[]): SpecsResult {
    const specs: Spec[] = [];
    const errors: ValidationError[] = [];
    const seen = new Set<string>();
    for (const value of raw) {
      const definition = this.parameters.get(value.key);
      if (seen.has(value.key)) {
        errors.push(new ValidationError(`specs.${value.key}`, 'declared twice'));
      } else if (definition === undefined) {
        errors.push(
          new ValidationError(`specs.${value.key}`, `unknown parameter for ${this.slug}`),
        );
      } else {
        const created = definition.createSpec(value);
        if (created instanceof ValidationError) {
          errors.push(created);
        } else {
          specs.push(created);
        }
      }
      seen.add(value.key);
    }
    for (const definition of this.parameters.values()) {
      if (definition.required && !seen.has(definition.key)) {
        errors.push(new ValidationError(`specs.${definition.key}`, 'required parameter missing'));
      }
    }
    return errors.length > 0 ? { ok: false, errors } : { ok: true, specs };
  }
}
