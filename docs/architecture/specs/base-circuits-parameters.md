# Base circuits — typed parameters (v1)

> **Feature**: issue #2 — domain class diagram and typed parameters (milestone M0)
> **Realized by**: [04-class.md](../diagrams/catalogue/04-class.md)
> **Use cases served**: UC2 (spec diff), UC3 (inspect), UC4 (find by need), UC6 (validate on publish)

## Purpose

Each base circuit defines the parameters its blocks must declare. This file is the source of
truth for those definitions: the `meta.yaml` schema (issue #5) and the domain classes implement
it. Blocks of a base circuit may only declare the parameters listed for it.

## Conventions

- **Storage in SI units**: values are stored in the SI unit of their quantity (V, A, Ω, Hz, W).
  In `meta.yaml` the curator may write a prefixed unit (`20 mA`, `4.7 kΩ`); the reader converts
  it to SI and the domain rejects a unit of the wrong quantity. Display units are a presentation
  concern.
- **Ranges**: every numeric spec is a closed range `[min, max]`; a single value is `min = max`.
- **Match mode** — how a search criterion (UC4) is compared with a block's spec:
  - `covers`: the block's range must **contain** the requested value or range. Used for what
    the circuit **accepts or withstands** (input voltage, maximum load current).
    _Example_: a regulator accepting 7–15 V matches a request for 12 V.
  - `within`: the block's range must **lie inside** the requested window. Used for what the
    circuit **delivers or is** (output voltage, cutoff frequency).
    _Example_: a regulator delivering 5 V matches a request for 4.9–5.1 V, not one for 3.3 V.
- **Enumerations** match when the block's value is one of the requested values; their Match
  column shows `—`.
- **Open-ended requests** use a point or a bounded range, never infinity: "at least 1 A" on a
  `covers` parameter is the point `[1, 1]`; "at most 3.3 V" on a `within` parameter is `[0, 3.3]`.
- **Same key, same meaning**: a key used by several base circuits (e.g. `inputVoltage`) has the
  same quantity and match mode everywhere, so a search can span base circuits.
- **Required**: a required parameter must be declared by every block of the base circuit.

## Quantities

| Quantity | SI unit | Symbol |
| --- | --- | --- |
| Voltage | volt | V |
| Current | ampere | A |
| Resistance | ohm | Ω |
| Frequency | hertz | Hz |
| Power | watt | W |
| Count | — (positive integer) | — |

## 1. LED + current-limiting resistor (`led-resistor`, order 1)

| Key | Label | Type | Match | Required |
| --- | --- | --- | --- | --- |
| `supplyVoltage` | Supply voltage | Voltage | covers | yes |
| `ledCurrent` | LED current | Current | within | yes |
| `ledColor` | LED colour | enum: `red`, `green`, `yellow`, `blue`, `white`, `infrared`, `rgb` | — | yes |
| `ledCount` | Number of LEDs | Count | within | yes |
| `resistorPower` | Resistor dissipation | Power | within | no |

Design formula (shown in v1, evaluated by the v2 calculator): `R = (supplyVoltage − n·Vf) / ledCurrent` for `n`
LEDs in series.

## 2. Voltage divider (`voltage-divider`, order 2)

| Key | Label | Type | Match | Required |
| --- | --- | --- | --- | --- |
| `inputVoltage` | Input voltage | Voltage | covers | yes |
| `outputVoltage` | Output voltage | Voltage | within | yes |
| `totalResistance` | Total resistance | Resistance | within | yes |
| `lowerElement` | Lower element | enum: `fixed`, `potentiometer`, `ldr`, `thermistor` | — | yes |

Design formula: `Vout = Vin · R2 / (R1 + R2)`.

## 3. RC filter (`rc-filter`, order 3)

| Key | Label | Type | Match | Required |
| --- | --- | --- | --- | --- |
| `filterType` | Filter type | enum: `low-pass`, `high-pass` | — | yes |
| `cutoffFrequency` | Cutoff frequency | Frequency | within | yes |
| `filterOrder` | Filter order | Count | within | yes |
| `inputVoltage` | Input voltage | Voltage | covers | no |

Design formula: `fc = 1 / (2π·R·C)` for a first-order filter.

## 4. Transistor switch (`transistor-switch`, order 4)

| Key | Label | Type | Match | Required |
| --- | --- | --- | --- | --- |
| `switchType` | Switching device | enum: `npn`, `pnp`, `n-mosfet`, `p-mosfet` | — | yes |
| `controlVoltage` | Control voltage | Voltage | covers | yes |
| `loadVoltage` | Load supply voltage | Voltage | covers | yes |
| `loadCurrent` | Load current | Current | covers | yes |
| `loadKind` | Load kind | enum: `resistive`, `inductive`, `led` | — | yes |

Design formula (bipolar): `Rb = (controlVoltage − Vbe) / (loadCurrent / hFE · k)` with an
overdrive factor `k` (typically 3–10).

## 5. Linear regulator (`linear-regulator`, order 5)

| Key | Label | Type | Match | Required |
| --- | --- | --- | --- | --- |
| `outputMode` | Output mode | enum: `fixed`, `adjustable`, `constant-current` | — | yes |
| `inputVoltage` | Input voltage | Voltage | covers | yes |
| `outputVoltage` | Output voltage | Voltage | within | no — absent for `constant-current` |
| `outputCurrent` | Maximum output current (capacity) | Current | covers | no — absent for `constant-current` |
| `regulatedCurrent` | Regulated current (setpoint) | Current | within | no — only for `constant-current` |
| `dropoutVoltage` | Dropout voltage | Voltage | within | no |

Design formulas: LM317 adjustable `Vout = 1.25 · (1 + R2/R1)`; constant current
`I = 1.25 / R`.

## Open points

- `outputCurrent` and `regulatedCurrent` are two parameters because they mean different things:
  the capacity a voltage regulator can supply (`covers`: "at least 500 mA") and the current a
  constant-current source imposes (`within`: "between 18 and 22 mA"). One parameter could not
  match both kinds of request correctly.
- `outputVoltage` is optional rather than "required unless constant-current": a conditional
  requirement would need a dedicated mechanism for a single case in v1 (YAGNI).
- Hazardous voltage is declared per block by the curator; none of the five v1 base circuits is
  hazardous by design, but a variant could be (e.g. mains-powered LED).
