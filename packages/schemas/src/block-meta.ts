/**
 * Reads a block's `meta.yaml` (docs/architecture/specs/catalogue-format.md): checks its shape
 * with Zod and converts spec values to SI. Domain rules (known keys, parent, variant summary)
 * are checked later by the domain classes.
 */
import { parseDocument } from 'yaml';
import * as z from 'zod';

import { parseSpecValue, type RawSpecValue } from './spec-value.js';

const slug = z.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/, 'must be kebab-case');
const nonEmpty = z.string().trim().min(1, 'must not be empty');

/** One spec of a block, keyed by parameter. */
export interface RawSpec {
  readonly key: string;
  readonly value: RawSpecValue;
}

/**
 * Spec values arrive as the exact text the curator wrote (see `readSpecTexts`). Every entry is
 * checked here, one issue per key, so no invalid entry hides the others.
 */
const SPEC_KEY = /^[a-z][a-zA-Z0-9]*$/;

const specsSchema = z
  .record(z.string(), z.unknown())
  .transform((specs, context): readonly RawSpec[] => {
    const entries = Object.entries(specs);
    if (entries.length === 0) {
      context.addIssue({ code: 'custom', message: 'must declare at least one spec', path: [] });
    }
    const converted: RawSpec[] = [];
    for (const [key, written] of entries) {
      if (!SPEC_KEY.test(key)) {
        context.addIssue({ code: 'custom', message: 'key must be camelCase', path: [key] });
      } else if (typeof written !== 'string') {
        context.addIssue({
          code: 'custom',
          message: 'must be a value with a unit, an integer or a lowercase word',
          path: [key],
        });
      } else {
        const parsed = parseSpecValue(written);
        if (parsed.ok) {
          converted.push({ key, value: parsed.value });
        } else {
          context.addIssue({ code: 'custom', message: parsed.error, path: [key] });
        }
      }
    }
    return converted;
  });

const blockMetaSchema = z.strictObject({
  slug,
  name: nonEmpty,
  description: nonEmpty,
  baseCircuit: slug,
  parent: slug.optional(),
  changeSummary: nonEmpty.optional(),
  difficulty: z.enum(['beginner', 'intermediate', 'advanced']),
  validationStatus: z.enum(['tested', 'theoretical']),
  hazardous: z.boolean(),
  specs: specsSchema,
  keyComponents: z.array(z.strictObject({ partNumber: nonEmpty, role: nonEmpty })).default([]),
  source: z.strictObject({
    title: nonEmpty,
    url: z.url({ protocol: /^https?$/ }).optional(),
  }),
});

/** The raw input of the domain's `BlockDraft`, as read from `meta.yaml`. */
export type BlockMeta = Readonly<z.infer<typeof blockMetaSchema>>;

export interface ReadError {
  /** Dotted path of the field, e.g. `specs.ledCurrent`; empty for a whole-file error. */
  readonly field: string;
  readonly message: string;
}

export type BlockMetaResult =
  | { readonly ok: true; readonly meta: BlockMeta }
  | { readonly ok: false; readonly errors: readonly ReadError[] };

/**
 * Returns the `specs` mapping with every scalar kept as the exact text written, so that YAML
 * never turns `1e3`, `1.0` or `0x10` into numbers before the notation is checked. Returns
 * undefined when `specs` is missing or not a mapping, leaving that error to the schema.
 */
function readSpecTexts(yamlText: string): unknown {
  const raw: unknown = parseDocument(yamlText, { schema: 'failsafe' }).toJS();
  const specs = typeof raw === 'object' && raw !== null && 'specs' in raw ? raw.specs : undefined;
  return typeof specs === 'object' && specs !== null ? specs : undefined;
}

/** Reads one `meta.yaml` text and reports every error found, never only the first. */
export function readBlockMeta(yamlText: string): BlockMetaResult {
  const document = parseDocument(yamlText);
  if (document.errors.length > 0) {
    return {
      ok: false,
      errors: document.errors.map((error) => ({
        field: '',
        message: `invalid YAML: ${error.message}`,
      })),
    };
  }

  const content: unknown = document.toJS();
  const specTexts = readSpecTexts(yamlText);
  const input =
    typeof content === 'object' && content !== null && specTexts !== undefined
      ? { ...content, specs: specTexts }
      : content;

  const result = blockMetaSchema.safeParse(input);
  if (!result.success) {
    return {
      ok: false,
      errors: result.error.issues.map((issue) => ({
        field: issue.path.join('.'),
        message: issue.message,
      })),
    };
  }
  return { ok: true, meta: result.data };
}
