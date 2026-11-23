import { BASE_CIRCUITS, Catalogue, type BlockDraft } from '@ohm-sweet-ohm/domain';

/** A catalogue holding the LED block and one variant, as the API tests expect it. */
export function makeCatalogue(): Catalogue {
  const catalogue = new Catalogue(BASE_CIRCUITS);
  const root: BlockDraft = {
    slug: 'led-resistor-basic',
    name: 'LED with current-limiting resistor',
    description: 'A red LED on 5 V through 220 Ω.',
    baseCircuitSlug: 'led-resistor',
    difficulty: 'BEGINNER',
    validationStatus: 'THEORETICAL',
    hazardous: false,
    rawSpecs: [
      { key: 'supplyVoltage', min: 5, max: 5, quantity: 'VOLTAGE' },
      { key: 'ledCurrent', min: 0.0136, max: 0.0136, quantity: 'CURRENT' },
      { key: 'ledColor', text: 'red' },
      { key: 'ledCount', min: 1, max: 1 },
    ],
    keyComponents: [{ partNumber: 'LTL-307EE', role: 'LED' }],
    source: { title: 'Ohm Sweet Ohm original design' },
    schematic: { kicadPath: 'led/schematic.kicad_sch', svgPath: 'led/schematic.svg' },
  };
  const errors = [
    ...catalogue.publish(root),
    ...catalogue.publish({
      ...root,
      slug: 'led-pair',
      parentSlug: 'led-resistor-basic',
      changeSummary: 'Two LEDs in series',
    }),
  ];
  if (errors.length > 0) throw new Error(JSON.stringify(errors));
  return catalogue;
}
