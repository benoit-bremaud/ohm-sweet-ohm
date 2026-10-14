import type { BlockDraft, Difficulty, RawSpec, ValidationStatus } from '@ohm-sweet-ohm/domain';
import type { BlockMeta, RawSpec as MetaSpec } from '@ohm-sweet-ohm/schemas';

const DIFFICULTY: Readonly<Record<BlockMeta['difficulty'], Difficulty>> = {
  beginner: 'BEGINNER',
  intermediate: 'INTERMEDIATE',
  advanced: 'ADVANCED',
};

const VALIDATION_STATUS: Readonly<Record<BlockMeta['validationStatus'], ValidationStatus>> = {
  tested: 'TESTED',
  theoretical: 'THEORETICAL',
};

/** Where a block's files live, relative to the catalogue and render roots. */
export interface BlockLocation {
  /** `<base-circuit>/<block>`, the same under `catalogue/` and the render output. */
  readonly relativeDir: string;
}

/** Turns the shape-checked `meta.yaml` of a block into the raw input of `Catalogue.publish`. */
export function toDraft(meta: BlockMeta, location: BlockLocation): BlockDraft {
  return {
    slug: meta.slug,
    name: meta.name,
    description: meta.description,
    ...(meta.changeSummary === undefined ? {} : { changeSummary: meta.changeSummary }),
    baseCircuitSlug: meta.baseCircuit,
    ...(meta.parent === undefined ? {} : { parentSlug: meta.parent }),
    difficulty: DIFFICULTY[meta.difficulty],
    validationStatus: VALIDATION_STATUS[meta.validationStatus],
    hazardous: meta.hazardous,
    rawSpecs: meta.specs.map(toRawSpec),
    keyComponents: meta.keyComponents,
    source: {
      title: meta.source.title,
      ...(meta.source.url === undefined ? {} : { url: meta.source.url }),
    },
    schematic: {
      kicadPath: `${location.relativeDir}/schematic.kicad_sch`,
      svgPath: `${location.relativeDir}/schematic.svg`,
    },
  };
}

function toRawSpec({ key, value }: MetaSpec): RawSpec {
  switch (value.kind) {
    case 'measure':
      return { key, min: value.min, max: value.max, quantity: value.quantity };
    case 'count':
      return { key, min: value.value, max: value.value };
    case 'text':
      return { key, text: value.text };
  }
}
