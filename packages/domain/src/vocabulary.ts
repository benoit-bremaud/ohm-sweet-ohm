/** Physical quantity of a numeric parameter; values are stored in its SI unit. */
export const QUANTITIES = [
  'VOLTAGE',
  'CURRENT',
  'RESISTANCE',
  'FREQUENCY',
  'POWER',
  'COUNT',
] as const;
export type Quantity = (typeof QUANTITIES)[number];

/**
 * How a search criterion is compared with a spec (base-circuits-parameters.md): `COVERS` for what
 * a circuit accepts or withstands, `WITHIN` for what it delivers.
 */
export type MatchMode = 'COVERS' | 'WITHIN';

/** How hard a block is to build, from the curator's point of view. */
export const DIFFICULTIES = ['BEGINNER', 'INTERMEDIATE', 'ADVANCED'] as const;
export type Difficulty = (typeof DIFFICULTIES)[number];

/** Whether a block was built and measured, or only designed. */
export const VALIDATION_STATUSES = ['TESTED', 'THEORETICAL'] as const;
export type ValidationStatus = (typeof VALIDATION_STATUSES)[number];
