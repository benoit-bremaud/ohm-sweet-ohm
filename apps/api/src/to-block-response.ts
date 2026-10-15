import { type Block, EnumSpec, NumericSpec, type Quantity, type Spec } from '@ohm-sweet-ohm/domain';
import type { BlockResponse } from '@ohm-sweet-ohm/schemas';

const UNIT: Readonly<Record<Quantity, string | null>> = {
  VOLTAGE: 'V',
  CURRENT: 'A',
  RESISTANCE: 'Ω',
  FREQUENCY: 'Hz',
  POWER: 'W',
  COUNT: null,
};

const lower = <T extends string>(value: T): Lowercase<T> => value.toLowerCase() as Lowercase<T>;

/** Translates a domain block into the public API contract (lowercase values, SI units). */
export function toBlockResponse(block: Block): BlockResponse {
  return {
    slug: block.slug,
    name: block.name,
    description: block.description,
    changeSummary: block.changeSummary ?? null,
    difficulty: lower(block.difficulty),
    validationStatus: lower(block.validationStatus),
    hazardous: block.hazardous,
    baseCircuit: { slug: block.baseCircuit.slug, name: block.baseCircuit.name },
    path: block.path().map((step) => ({ slug: step.slug, name: step.name })),
    specs: block.specs.map(toSpecResponse),
    keyComponents: block.keyComponents.map(({ partNumber, role }) => ({ partNumber, role })),
    source: { title: block.source.title, url: block.source.url ?? null },
    formulas: block.baseCircuit.formulas.map(({ name, expression, description }) => ({
      name,
      expression,
      description,
    })),
    schematicUrl: `/blocks/${block.slug}/schematic.svg`,
  };
}

// The boundary reads the two concrete spec kinds; the domain stays unaware of the API format.
function toSpecResponse(spec: Spec): BlockResponse['specs'][number] {
  const label = spec.definition.label;
  if (spec instanceof NumericSpec) {
    const { quantity } = spec.definition;
    return {
      key: spec.key,
      label,
      kind: 'number',
      quantity: lower(quantity),
      unit: UNIT[quantity],
      min: spec.range.min,
      max: spec.range.max,
    };
  }
  if (spec instanceof EnumSpec) {
    return { key: spec.key, label, kind: 'enum', value: spec.value };
  }
  throw new Error(`unsupported spec kind for ${spec.key}`);
}
