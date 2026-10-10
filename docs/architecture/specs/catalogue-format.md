# Catalogue format — blocks on disk (v1)

> **Feature**: issue #5 — `meta.yaml` schema and LED example block (milestone M0)
> **Serves**: UC6 (publish a block) through the importer
> **Related**: [base-circuits-parameters.md](base-circuits-parameters.md),
> [04-class.md](../diagrams/catalogue/04-class.md) (`BlockDraft`, `RawSpec`)

## Purpose

This file defines how a curator writes a block in the repository. The reader in
`packages/schemas` checks the **shape** of each file and converts spec values to SI units. It
produces the raw input of the domain (`BlockDraft`, `RawSpec`). Domain rules — known parameter
keys, required parameters, parent and variant tree, change summary of a variant — are checked by
the domain classes, not here.

## Layout

```text
catalogue/
  LICENSE                              CC BY-SA 4.0, covers every file below
  <base-circuit-slug>/
    <block-slug>/
      meta.yaml                        block metadata (this format)
      schematic.kicad_sch              KiCad 9 schematic of the block
```

- Blocks are grouped by base circuit. The variant tree is declared by `parent` in `meta.yaml`,
  never by the folder structure, so moving a variant never moves a folder.
- The folder name of a block equals its `slug`.

## `meta.yaml`

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `slug` | string, kebab-case | yes | Unique across the catalogue; equals the folder name |
| `name` | string | yes | Display name |
| `description` | string | yes | What the block does, in plain words |
| `baseCircuit` | string, kebab-case | yes | Slug of the base circuit, e.g. `led-resistor` |
| `parent` | string, kebab-case | no | Slug of the parent block; absent for the root block |
| `changeSummary` | string | no | What the variant changes; required by the domain for a variant |
| `difficulty` | `beginner` \| `intermediate` \| `advanced` | yes | |
| `validationStatus` | `tested` \| `theoretical` | yes | `tested` means built and measured |
| `hazardous` | boolean | yes | `true` when the block involves hazardous voltage |
| `specs` | map of parameter key to value | yes, at least one | Values below |
| `keyComponents` | list of `{ partNumber, role }` | no, default empty | |
| `source` | `{ title, url? }` | yes | `url` must be an absolute http(s) URL |

Unknown fields are rejected, so a typo never goes unnoticed.

## Spec values

| Written as | Meaning | Example |
| --- | --- | --- |
| `<number> <unit>` | A single value | `ledCurrent: 13.6 mA` |
| `<number> <unit> .. <number> <unit>` | A closed range; both ends carry a unit of the same quantity | `inputVoltage: 7 V .. 15 V` |
| `<integer>` | A count, no unit | `ledCount: 1` |
| `<word>` | An enumeration value: lowercase letters and digits in segments joined by single hyphens | `ledColor: red`, `filterType: low-pass` |

- **Units**: `V`, `A`, `Ω` (also `ohm`), `Hz`, `W`.
- **Prefixes**: `p`, `n`, `µ` (also `u`), `m`, `k`, `M`, `G`. A space between number and unit is
  optional.
- **Numbers**: decimal point `.` with digits on both sides, optional sign; no exponent, comma or
  hexadecimal notation.
- **Words**: `red-`, `red--blue` or `Red` are rejected with a message showing the expected form.
- **Read as written**: spec values are checked as the exact text in the file, so YAML never turns
  `1e3` or `1.0` into a number first. Quoting a value is never needed.
- Values are converted to SI by shifting the decimal point (`13.6 mA` reads as `13.6e-3`), so the
  stored number is the closest one to what was written, with no rounding step: `4.7 kΩ` is
  stored as `4700` ohms and `13.6 mA` as `0.0136` A.
- At most **15 significant digits** per number, so two different written values always stay
  different and correctly ordered.
- A value too large, too small to stay exact, or written as non-zero but converting to zero is
  rejected as out of range. Overflow and underflow never pass silently.
- A single value is read as a range whose ends are equal: `5 V` and `5 V .. 5 V` mean the same.
- A range must satisfy `min ≤ max`, checked on the converted values; an unknown unit, a missing unit on one end, or units of
  different quantities are errors.
- Whether a parameter expects a number, a count or an enumeration value is a domain rule, checked
  against the base circuit's definitions. For example a bare `ohm` reads as a word here, and the
  domain rejects it for a numeric parameter. Likewise `true`, `null` or `yes` read as plain words, never as YAML
  booleans or null, and only match an enumeration that defines them.

## Errors

The reader never stops at the first problem: it reports every error with the path of the field,
for example `specs.ledCurrent: unknown unit "mAh"`.
