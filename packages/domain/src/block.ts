import type { BaseCircuit } from './base-circuit.js';
import type { RawSpec, Spec } from './specs.js';
import type { Difficulty, ValidationStatus } from './vocabulary.js';

export interface KeyComponent {
  readonly partNumber: string;
  readonly role: string;
}

export interface Source {
  readonly title: string;
  readonly url?: string;
}

/** Where the block's KiCad schematic and its rendered, cropped SVG live. */
export interface SchematicAsset {
  readonly kicadPath: string;
  readonly svgPath: string;
}

/** What a curator submits for publication (UC6): slugs and untyped values, checked by the catalogue. */
export interface BlockDraft {
  readonly slug: string;
  readonly name: string;
  readonly description: string;
  readonly changeSummary?: string;
  readonly baseCircuitSlug: string;
  readonly parentSlug?: string;
  readonly difficulty: Difficulty;
  readonly validationStatus: ValidationStatus;
  readonly hazardous: boolean;
  readonly rawSpecs: readonly RawSpec[];
  readonly keyComponents: readonly KeyComponent[];
  readonly source: Source;
  readonly schematic: SchematicAsset;
}

export interface BlockProperties {
  readonly slug: string;
  readonly name: string;
  readonly description: string;
  readonly changeSummary?: string;
  readonly difficulty: Difficulty;
  readonly validationStatus: ValidationStatus;
  readonly hazardous: boolean;
  readonly baseCircuit: BaseCircuit;
  readonly parent?: Block;
  readonly specs: readonly Spec[];
  readonly keyComponents: readonly KeyComponent[];
  readonly source: Source;
  readonly schematic: SchematicAsset;
}

/** A published circuit block: a root block of its base circuit, or a variant of another block. */
export class Block {
  readonly slug: string;
  readonly name: string;
  readonly description: string;
  readonly changeSummary: string | undefined;
  readonly difficulty: Difficulty;
  readonly validationStatus: ValidationStatus;
  readonly hazardous: boolean;
  readonly baseCircuit: BaseCircuit;
  readonly parent: Block | undefined;
  readonly specs: readonly Spec[];
  readonly keyComponents: readonly KeyComponent[];
  readonly source: Source;
  readonly schematic: SchematicAsset;

  constructor(properties: BlockProperties) {
    const hasSummary = (properties.changeSummary?.trim() ?? '') !== '';
    if ((properties.parent === undefined) !== !hasSummary) {
      throw new RangeError(
        `block ${properties.slug}: a variant needs a change summary, a root block none`,
      );
    }
    this.slug = properties.slug;
    this.name = properties.name;
    this.description = properties.description;
    this.changeSummary = properties.changeSummary;
    this.difficulty = properties.difficulty;
    this.validationStatus = properties.validationStatus;
    this.hazardous = properties.hazardous;
    this.baseCircuit = properties.baseCircuit;
    this.parent = properties.parent;
    this.specs = properties.specs;
    this.keyComponents = properties.keyComponents;
    this.source = properties.source;
    this.schematic = properties.schematic;
  }

  isVariant(): boolean {
    return this.parent !== undefined;
  }

  /** The variant path from the base circuit's root block down to this block (UC2 breadcrumb). */
  path(): readonly Block[] {
    return this.parent === undefined ? [this] : [...this.parent.path(), this];
  }

  specFor(key: string): Spec | undefined {
    return this.specs.find((spec) => spec.key === key);
  }

  /** The same block attached to another parent object, used when its parent is republished. */
  withParent(parent: Block): Block {
    return new Block({ ...this.properties(), parent });
  }

  private properties(): BlockProperties {
    return {
      slug: this.slug,
      name: this.name,
      description: this.description,
      ...(this.changeSummary === undefined ? {} : { changeSummary: this.changeSummary }),
      difficulty: this.difficulty,
      validationStatus: this.validationStatus,
      hazardous: this.hazardous,
      baseCircuit: this.baseCircuit,
      ...(this.parent === undefined ? {} : { parent: this.parent }),
      specs: this.specs,
      keyComponents: this.keyComponents,
      source: this.source,
      schematic: this.schematic,
    };
  }
}
