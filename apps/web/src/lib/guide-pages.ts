import type { MarkdownHeading } from 'astro';
import { getCollection } from 'astro:content';

/** One prerendered page per guide, its route segment the guide folder. */
export async function guidePaths() {
  const guides = await getCollection('guides');
  return guides.map((guide) => ({ params: { guide: guide.id }, props: { guide } }));
}

/** Title of a guide: its level 1 heading, required so no page goes out titled by its folder. */
export function guideTitle(headings: readonly MarkdownHeading[], id: string): string {
  const title = headings.find((h) => h.depth === 1)?.text;
  if (title === undefined) throw new Error(`guide ${id} has no level 1 heading`);
  return title;
}
