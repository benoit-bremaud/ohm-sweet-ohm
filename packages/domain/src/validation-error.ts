/** A domain rule broken by some input, reported to the curator with the field it concerns. */
export class ValidationError {
  constructor(
    /** Dotted path of the field, e.g. `specs.ledCurrent`; empty for the whole draft. */
    readonly field: string,
    readonly message: string,
  ) {}
}
