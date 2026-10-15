/**
 * Public API contract of a block (GET /blocks/{slug}), shared by the API, which validates and
 * documents its responses with it, and the web front-end. Enumerated values are lowercase, like
 * the catalogue files and the spec values; numbers are in SI units with their unit symbol.
 */
import * as z from 'zod';

const reference = z.object({
  slug: z.string().describe('Stable identifier, kebab-case'),
  name: z.string(),
});

const numericSpec = z.object({
  key: z.string(),
  label: z.string(),
  kind: z.literal('number'),
  quantity: z.enum(['voltage', 'current', 'resistance', 'frequency', 'power', 'count']),
  unit: z.string().nullable().describe('SI unit symbol, null for a count'),
  min: z.number(),
  max: z.number().describe('Equal to min for a single value'),
});

const enumSpec = z.object({
  key: z.string(),
  label: z.string(),
  kind: z.literal('enum'),
  value: z.string(),
});

export const blockResponseSchema = z
  .object({
    slug: z.string(),
    name: z.string(),
    description: z.string(),
    changeSummary: z
      .string()
      .nullable()
      .describe('What this variant changes; null for a root block'),
    difficulty: z.enum(['beginner', 'intermediate', 'advanced']),
    validationStatus: z.enum(['tested', 'theoretical']),
    hazardous: z.boolean().describe('True when the block involves hazardous voltage'),
    baseCircuit: reference,
    path: z.array(reference).describe('From the base circuit root block down to this block'),
    specs: z.array(z.discriminatedUnion('kind', [numericSpec, enumSpec])),
    keyComponents: z.array(z.object({ partNumber: z.string(), role: z.string() })),
    source: z.object({ title: z.string(), url: z.string().nullable() }),
    formulas: z.array(
      z.object({ name: z.string(), expression: z.string(), description: z.string() }),
    ),
    schematicUrl: z.string().describe('Path of the rendered, cropped SVG schematic'),
  })
  .describe('A published circuit block');

export type BlockResponse = z.infer<typeof blockResponseSchema>;

export const errorResponseSchema = z.object({ error: z.string() }).describe('An error');
