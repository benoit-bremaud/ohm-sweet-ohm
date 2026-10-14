import type { BaseCircuit } from '../base-circuit.js';
import { ledResistor } from './led-resistor.js';

/** Every base circuit of the catalogue, in progression order; one is added per milestone. */
export const BASE_CIRCUITS: readonly BaseCircuit[] = [ledResistor];
