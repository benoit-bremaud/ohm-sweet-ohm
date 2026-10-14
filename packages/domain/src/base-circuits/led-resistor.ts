import { BaseCircuit, Formula } from '../base-circuit.js';
import { EnumParameterDefinition, NumericParameterDefinition } from '../specs.js';

/** Base circuit 1 (base-circuits-parameters.md §1): an LED with its current-limiting resistor. */
export const ledResistor = new BaseCircuit(
  'led-resistor',
  'LED with current-limiting resistor',
  1,
  [
    new NumericParameterDefinition('supplyVoltage', 'Supply voltage', true, 'VOLTAGE', 'COVERS'),
    new NumericParameterDefinition('ledCurrent', 'LED current', true, 'CURRENT', 'WITHIN'),
    new EnumParameterDefinition('ledColor', 'LED colour', true, [
      'red',
      'green',
      'yellow',
      'blue',
      'white',
      'infrared',
      'rgb',
    ]),
    new NumericParameterDefinition('ledCount', 'Number of LEDs', true, 'COUNT', 'WITHIN'),
    new NumericParameterDefinition(
      'resistorPower',
      'Resistor dissipation',
      false,
      'POWER',
      'WITHIN',
    ),
  ],
  [
    new Formula(
      'Series resistor',
      'R = (supplyVoltage − n·Vf) / ledCurrent',
      'Resistance that sets the LED current for n LEDs in series, each dropping Vf.',
    ),
  ],
);
