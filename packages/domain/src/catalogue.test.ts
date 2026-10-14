import { describe, expect, it } from 'vitest';

import { BaseCircuit } from './base-circuit.js';
import { ledResistor } from './base-circuits/led-resistor.js';
import type { BlockDraft } from './block.js';
import { Catalogue } from './catalogue.js';
import {
  EnumParameterDefinition,
  NumericParameterDefinition,
  NumericSpec,
  type RawSpec,
} from './specs.js';

const LED_SPECS: readonly RawSpec[] = [
  { key: 'supplyVoltage', min: 5, max: 5, quantity: 'VOLTAGE' },
  { key: 'ledCurrent', min: 0.0136, max: 0.0136, quantity: 'CURRENT' },
  { key: 'ledColor', text: 'red' },
  { key: 'ledCount', min: 1, max: 1 },
];

function draft(overrides: Partial<BlockDraft> = {}): BlockDraft {
  return {
    slug: 'led-resistor-basic',
    name: 'LED with current-limiting resistor',
    description: 'A red LED on 5 V through 220 Ω.',
    baseCircuitSlug: 'led-resistor',
    difficulty: 'BEGINNER',
    validationStatus: 'THEORETICAL',
    hazardous: false,
    rawSpecs: LED_SPECS,
    keyComponents: [],
    source: { title: 'Ohm Sweet Ohm original design' },
    schematic: { kicadPath: 'catalogue/led/schematic.kicad_sch', svgPath: 'led/schematic.svg' },
    ...overrides,
  };
}

function variant(
  slug: string,
  parentSlug: string,
  overrides: Partial<BlockDraft> = {},
): BlockDraft {
  return draft({ slug, parentSlug, changeSummary: `${slug} change`, ...overrides });
}

function fields(errors: readonly { field: string }[]): readonly string[] {
  return errors.map((error) => error.field);
}

describe('Catalogue.publish', () => {
  it('publishes a valid root block with typed specs', () => {
    const catalogue = new Catalogue([ledResistor]);

    const errors = catalogue.publish(draft());

    const block = catalogue.findBlock('led-resistor-basic');
    expect(errors).toEqual([]);
    expect(block?.isVariant()).toBe(false);
    expect(block?.specFor('ledCurrent')).toBeInstanceOf(NumericSpec);
  });

  it('reports every broken rule of a draft at once and leaves the catalogue unchanged', () => {
    const catalogue = new Catalogue([ledResistor]);

    const errors = catalogue.publish(
      draft({
        rawSpecs: [
          { key: 'supplyVoltage', min: 5, max: 5, quantity: 'CURRENT' },
          { key: 'unknownKey', text: 'x' },
          { key: 'ledColor', text: 'purple' },
        ],
        parentSlug: 'missing-parent',
      }),
    );

    expect(fields(errors)).toEqual([
      'specs.supplyVoltage',
      'specs.unknownKey',
      'specs.ledColor',
      'specs.ledCurrent',
      'specs.ledCount',
      'parent',
      'changeSummary',
    ]);
    expect(catalogue.findBlock('led-resistor-basic')).toBeUndefined();
  });

  it('reports a duplicate spec key', () => {
    const catalogue = new Catalogue([ledResistor]);

    const errors = catalogue.publish(
      draft({ rawSpecs: [...LED_SPECS, { key: 'ledColor', text: 'green' }] }),
    );

    expect(errors).toEqual([
      expect.objectContaining({ field: 'specs.ledColor', message: 'declared twice' }),
    ]);
  });

  it('reports an unknown key declared twice once as unknown, then as a duplicate', () => {
    const catalogue = new Catalogue([ledResistor]);

    const errors = catalogue.publish(
      draft({ rawSpecs: [...LED_SPECS, { key: 'typo', text: 'x' }, { key: 'typo', text: 'y' }] }),
    );

    expect(errors.map((error) => error.message)).toEqual([
      'unknown parameter for led-resistor',
      'declared twice',
    ]);
  });

  it('rejects an unknown base circuit', () => {
    const catalogue = new Catalogue([ledResistor]);

    expect(fields(catalogue.publish(draft({ baseCircuitSlug: 'nope' })))).toEqual(['baseCircuit']);
  });

  it('accepts a variant with a change summary and builds its path', () => {
    const catalogue = new Catalogue([ledResistor]);
    catalogue.publish(draft());

    const errors = catalogue.publish(variant('led-two-in-series', 'led-resistor-basic'));

    expect(errors).toEqual([]);
    expect(
      catalogue
        .findBlock('led-two-in-series')
        ?.path()
        .map((block) => block.slug),
    ).toEqual(['led-resistor-basic', 'led-two-in-series']);
  });

  it.each([
    [draft({ changeSummary: 'not allowed' }), 'a root block has no change summary'],
    [
      draft({ slug: 'child', parentSlug: 'led-resistor-basic' }),
      'a variant needs a change summary',
    ],
  ])('enforces the change summary rule (%#)', (input, message) => {
    const catalogue = new Catalogue([ledResistor]);
    catalogue.publish(draft());

    expect(catalogue.publish(input)).toEqual([
      expect.objectContaining({ field: 'changeSummary', message }),
    ]);
  });

  it('treats a blank change summary as missing', () => {
    const catalogue = new Catalogue([ledResistor]);
    catalogue.publish(draft());

    const errors = catalogue.publish(variant('a', 'led-resistor-basic', { changeSummary: '   ' }));

    expect(errors).toEqual([
      expect.objectContaining({
        field: 'changeSummary',
        message: 'a variant needs a change summary',
      }),
    ]);
  });

  it('lets the root block be republished in place', () => {
    const catalogue = new Catalogue([ledResistor]);
    catalogue.publish(draft());

    expect(catalogue.publish(draft({ name: 'Renamed' }))).toEqual([]);
  });

  it('refuses to turn a variant into a second root while a root exists', () => {
    const catalogue = new Catalogue([ledResistor]);
    catalogue.publish(draft());
    catalogue.publish(variant('a', 'led-resistor-basic'));

    expect(fields(catalogue.publish(draft({ slug: 'a' })))).toEqual(['parent']);
  });

  it('allows at most one root block per base circuit', () => {
    const catalogue = new Catalogue([ledResistor]);
    catalogue.publish(draft());

    const errors = catalogue.publish(draft({ slug: 'second-root' }));

    expect(errors).toEqual([
      expect.objectContaining({
        field: 'parent',
        message: 'led-resistor already has the root block led-resistor-basic',
      }),
    ]);
  });

  it('rejects a parent from another base circuit', () => {
    const other = new BaseCircuit('other-circuit', 'Other', 2, [
      new NumericParameterDefinition('supplyVoltage', 'Supply voltage', true, 'VOLTAGE', 'COVERS'),
    ]);
    const catalogue = new Catalogue([ledResistor, other]);
    catalogue.publish(draft());
    catalogue.publish(
      draft({
        slug: 'other-root',
        baseCircuitSlug: 'other-circuit',
        rawSpecs: [{ key: 'supplyVoltage', min: 5, max: 5, quantity: 'VOLTAGE' }],
      }),
    );

    const errors = catalogue.publish(variant('led-child', 'other-root'));

    expect(errors).toEqual([
      expect.objectContaining({
        field: 'parent',
        message: 'parent other-root belongs to another base circuit',
      }),
    ]);
  });

  it('rejects a republication that would create a cycle', () => {
    const catalogue = new Catalogue([ledResistor]);
    catalogue.publish(draft());
    catalogue.publish(variant('a', 'led-resistor-basic'));
    catalogue.publish(variant('b', 'a'));

    const errors = catalogue.publish(variant('a', 'b'));

    expect(errors).toEqual([
      expect.objectContaining({
        field: 'parent',
        message: 'making b the parent would create a cycle',
      }),
    ]);
  });

  it('rejects a block declared as its own parent', () => {
    const catalogue = new Catalogue([ledResistor]);
    catalogue.publish(draft());
    catalogue.publish(variant('a', 'led-resistor-basic'));

    expect(fields(catalogue.publish(variant('a', 'a')))).toEqual(['parent']);
  });

  it('relinks variants to the republished parent', () => {
    const catalogue = new Catalogue([ledResistor]);
    catalogue.publish(draft());
    catalogue.publish(variant('a', 'led-resistor-basic'));
    catalogue.publish(variant('b', 'a'));

    catalogue.publish(draft({ name: 'Renamed root' }));

    expect(
      catalogue
        .findBlock('b')
        ?.path()
        .map((block) => block.name),
    ).toEqual([
      'Renamed root',
      'LED with current-limiting resistor',
      'LED with current-limiting resistor',
    ]);
    expect(catalogue.findBlock('b')?.parent).toBe(catalogue.findBlock('a'));
    expect(catalogue.findBlock('a')?.parent).toBe(catalogue.findBlock('led-resistor-basic'));
  });

  it('moves a variant and its descendants under another parent', () => {
    const catalogue = new Catalogue([ledResistor]);
    catalogue.publish(draft());
    catalogue.publish(variant('a', 'led-resistor-basic'));
    catalogue.publish(variant('b', 'a'));
    catalogue.publish(variant('c', 'led-resistor-basic'));

    const errors = catalogue.publish(variant('a', 'c', { changeSummary: 'moved under c' }));

    expect(errors).toEqual([]);
    expect(
      catalogue
        .findBlock('b')
        ?.path()
        .map((block) => block.slug),
    ).toEqual(['led-resistor-basic', 'c', 'a', 'b']);
  });

  it('refuses to move a block that has variants to another base circuit', () => {
    const other = new BaseCircuit('other-circuit', 'Other', 2, [
      new NumericParameterDefinition('supplyVoltage', 'Supply voltage', true, 'VOLTAGE', 'COVERS'),
    ]);
    const catalogue = new Catalogue([ledResistor, other]);
    catalogue.publish(draft());
    catalogue.publish(variant('a', 'led-resistor-basic'));

    const errors = catalogue.publish(
      draft({
        baseCircuitSlug: 'other-circuit',
        rawSpecs: [{ key: 'supplyVoltage', min: 5, max: 5, quantity: 'VOLTAGE' }],
      }),
    );

    expect(errors).toEqual([
      expect.objectContaining({
        field: 'baseCircuit',
        message: 'cannot change the base circuit of a block that has variants',
      }),
    ]);
  });
});

describe('Catalogue.publish across base circuits', () => {
  const other = new BaseCircuit('other-circuit', 'Other', 2, [
    new NumericParameterDefinition('supplyVoltage', 'Supply voltage', true, 'VOLTAGE', 'COVERS'),
  ]);
  const otherSpecs: readonly RawSpec[] = [
    { key: 'supplyVoltage', min: 5, max: 5, quantity: 'VOLTAGE' },
  ];

  it('moves a block without variants to another base circuit, freeing the old root', () => {
    const catalogue = new Catalogue([ledResistor, other]);
    catalogue.publish(draft());

    const moved = catalogue.publish(
      draft({ baseCircuitSlug: 'other-circuit', rawSpecs: otherSpecs }),
    );
    const newRoot = catalogue.publish(draft({ slug: 'new-led-root' }));

    expect([moved, newRoot]).toEqual([[], []]);
    expect(catalogue.findBlock('led-resistor-basic')?.baseCircuit).toBe(other);
  });

  it('reports an unknown base circuit without inventing a parent error', () => {
    const catalogue = new Catalogue([ledResistor, other]);
    catalogue.publish(draft());

    const errors = catalogue.publish(
      variant('a', 'led-resistor-basic', { baseCircuitSlug: 'nope' }),
    );

    expect(fields(errors)).toEqual(['baseCircuit']);
  });
});

describe('Catalogue construction', () => {
  it('refuses a shared key with different meanings', () => {
    const conflicting = new BaseCircuit('conflicting', 'Conflicting', 2, [
      new EnumParameterDefinition('ledColor', 'Colour', true, ['red']),
    ]);

    expect(() => new Catalogue([ledResistor, conflicting])).toThrow(
      /ledColor has different meanings/,
    );
  });

  it('refuses a base circuit defined twice', () => {
    expect(() => new Catalogue([ledResistor, ledResistor])).toThrow(/defined twice/);
  });
});
