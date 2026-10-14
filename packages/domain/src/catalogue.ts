import type { BaseCircuit } from './base-circuit.js';
import { Block, type BlockDraft } from './block.js';
import type { ParameterDefinition } from './specs.js';
import { ValidationError } from './validation-error.js';

/**
 * The aggregate root of the catalogue: base circuits and published blocks. Publication (UC6)
 * enforces every invariant of 04-class.md and reports all broken rules at once.
 */
export class Catalogue {
  private readonly baseCircuits: ReadonlyMap<string, BaseCircuit>;
  private readonly blocks = new Map<string, Block>();

  constructor(baseCircuits: readonly BaseCircuit[]) {
    const bySlug = new Map<string, BaseCircuit>();
    const definitions = new Map<string, ParameterDefinition>();
    for (const baseCircuit of baseCircuits) {
      if (bySlug.has(baseCircuit.slug)) {
        throw new RangeError(`base circuit ${baseCircuit.slug} is defined twice`);
      }
      bySlug.set(baseCircuit.slug, baseCircuit);
      for (const definition of baseCircuit.parameterDefinitions) {
        // Only the kind must match (04-class.md): labels and required flags may differ.
        const known = definitions.get(definition.key);
        if (known !== undefined && !known.sameKindAs(definition)) {
          throw new RangeError(
            `parameter ${definition.key} has different meanings across base circuits`,
          );
        }
        definitions.set(definition.key, definition);
      }
    }
    this.baseCircuits = bySlug;
  }

  findBlock(slug: string): Block | undefined {
    return this.blocks.get(slug);
  }

  findBaseCircuit(slug: string): BaseCircuit | undefined {
    return this.baseCircuits.get(slug);
  }

  /**
   * Publishes a block, replacing any previous version with the same slug. Returns every broken
   * rule; the catalogue is left unchanged unless the list is empty.
   */
  publish(draft: BlockDraft): readonly ValidationError[] {
    const errors: ValidationError[] = [];

    const baseCircuit = this.baseCircuits.get(draft.baseCircuitSlug);
    if (baseCircuit === undefined) {
      errors.push(
        new ValidationError('baseCircuit', `unknown base circuit "${draft.baseCircuitSlug}"`),
      );
    }
    const specs = baseCircuit?.specsFrom(draft.rawSpecs);
    if (specs !== undefined && !specs.ok) {
      errors.push(...specs.errors);
    }

    const parent = this.resolveParent(draft, baseCircuit, errors);

    // A blank summary counts as absent: a variant must say what it changes.
    const changeSummary = draft.changeSummary?.trim() === '' ? undefined : draft.changeSummary;
    if ((draft.parentSlug === undefined) !== (changeSummary === undefined)) {
      errors.push(
        new ValidationError(
          'changeSummary',
          draft.parentSlug === undefined
            ? 'a root block has no change summary'
            : 'a variant needs a change summary',
        ),
      );
    }

    if (baseCircuit !== undefined && draft.parentSlug === undefined) {
      const otherRoot = [...this.blocks.values()].find(
        (block) =>
          block.baseCircuit === baseCircuit && !block.isVariant() && block.slug !== draft.slug,
      );
      if (otherRoot !== undefined) {
        errors.push(
          new ValidationError(
            'parent',
            `${baseCircuit.slug} already has the root block ${otherRoot.slug}`,
          ),
        );
      }
    }

    const previous = this.blocks.get(draft.slug);
    if (
      previous !== undefined &&
      baseCircuit !== undefined &&
      previous.baseCircuit !== baseCircuit
    ) {
      if (this.childrenOf(previous.slug).length > 0) {
        errors.push(
          new ValidationError(
            'baseCircuit',
            'cannot change the base circuit of a block that has variants',
          ),
        );
      }
    }

    if (errors.length > 0 || baseCircuit === undefined || !specs?.ok) {
      return errors;
    }

    const block = new Block({
      slug: draft.slug,
      name: draft.name,
      description: draft.description,
      ...(changeSummary === undefined ? {} : { changeSummary }),
      difficulty: draft.difficulty,
      validationStatus: draft.validationStatus,
      hazardous: draft.hazardous,
      baseCircuit,
      ...(parent === undefined ? {} : { parent }),
      specs: specs.specs,
      keyComponents: draft.keyComponents,
      source: draft.source,
      schematic: draft.schematic,
    });
    this.blocks.set(block.slug, block);
    this.relinkDescendants(block);
    return [];
  }

  private resolveParent(
    draft: BlockDraft,
    baseCircuit: BaseCircuit | undefined,
    errors: ValidationError[],
  ): Block | undefined {
    if (draft.parentSlug === undefined) {
      return undefined;
    }
    const parent = this.blocks.get(draft.parentSlug);
    if (parent === undefined) {
      errors.push(new ValidationError('parent', `unknown parent block "${draft.parentSlug}"`));
      return undefined;
    }
    if (baseCircuit !== undefined && parent.baseCircuit !== baseCircuit) {
      errors.push(
        new ValidationError('parent', `parent ${parent.slug} belongs to another base circuit`),
      );
    }
    if (parent.path().some((ancestor) => ancestor.slug === draft.slug)) {
      errors.push(
        new ValidationError('parent', `making ${parent.slug} the parent would create a cycle`),
      );
    }
    return parent;
  }

  private childrenOf(slug: string): readonly Block[] {
    return [...this.blocks.values()].filter((block) => block.parent?.slug === slug);
  }

  /** Blocks are immutable: when a parent is republished, its descendants point to the new object. */
  private relinkDescendants(parent: Block): void {
    for (const child of this.childrenOf(parent.slug)) {
      const relinked = child.withParent(parent);
      this.blocks.set(relinked.slug, relinked);
      this.relinkDescendants(relinked);
    }
  }
}
