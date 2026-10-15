import type { BlockResponse } from '@ohm-sweet-ohm/schemas';

/** The LED block as the API returns it, for tests. */
export const LED_BLOCK: BlockResponse = {
  slug: 'led-resistor-basic',
  name: 'LED with current-limiting resistor',
  description: 'A single red LED driven from a 5 V supply through a 220 Ω resistor.',
  changeSummary: null,
  difficulty: 'beginner',
  validationStatus: 'theoretical',
  hazardous: false,
  baseCircuit: { slug: 'led-resistor', name: 'LED with current-limiting resistor' },
  path: [{ slug: 'led-resistor-basic', name: 'LED with current-limiting resistor' }],
  specs: [
    {
      key: 'supplyVoltage',
      label: 'Supply voltage',
      kind: 'number',
      quantity: 'voltage',
      unit: 'V',
      min: 5,
      max: 5,
    },
    {
      key: 'ledCurrent',
      label: 'LED current',
      kind: 'number',
      quantity: 'current',
      unit: 'A',
      min: 0.0136,
      max: 0.0136,
    },
    { key: 'ledColor', label: 'LED colour', kind: 'enum', value: 'red' },
    {
      key: 'ledCount',
      label: 'Number of LEDs',
      kind: 'number',
      quantity: 'count',
      unit: null,
      min: 1,
      max: 1,
    },
  ],
  keyComponents: [],
  source: { title: 'Ohm Sweet Ohm original design', url: null },
  formulas: [
    {
      name: 'Series resistor',
      expression: 'R = (supplyVoltage − n·Vf) / ledCurrent',
      description: 'Resistance that sets the LED current for n LEDs in series.',
    },
  ],
  schematicUrl: '/blocks/led-resistor-basic/schematic.svg',
};
