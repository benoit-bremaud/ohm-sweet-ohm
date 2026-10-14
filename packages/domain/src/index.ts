export { BaseCircuit, Formula, type SpecsResult } from './base-circuit.js';
export { BASE_CIRCUITS } from './base-circuits/index.js';
export { ledResistor } from './base-circuits/led-resistor.js';
export {
  Block,
  type BlockDraft,
  type BlockProperties,
  type KeyComponent,
  type SchematicAsset,
  type Source,
} from './block.js';
export { Catalogue } from './catalogue.js';
export { SpecRange } from './spec-range.js';
export {
  EnumParameterDefinition,
  EnumSpec,
  NumericParameterDefinition,
  NumericSpec,
  ParameterDefinition,
  type RawSpec,
  Spec,
} from './specs.js';
export { ValidationError } from './validation-error.js';
export {
  DIFFICULTIES,
  type Difficulty,
  type MatchMode,
  QUANTITIES,
  type Quantity,
  VALIDATION_STATUSES,
  type ValidationStatus,
} from './vocabulary.js';
