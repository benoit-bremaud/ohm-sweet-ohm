import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';

import { GUIDES_DIR } from './lib/guide-links';

// The troubleshooting guides are read in place from the repository's troubleshooting/ folder
// (epic #79): GitHub and the site render the same files, nothing is copied.
// Relative to the Astro project root (apps/web).
const base = `../../${GUIDES_DIR}`;

/** One entry per guide, its id the guide folder (`10_resistance`). */
const guides = defineCollection({
  loader: glob({
    base,
    pattern: '{[0-9][0-9],i[0-9]}_*/README.md',
    generateId: ({ entry }) => entry.split('/')[0] ?? entry,
  }),
});

/** The menu of the guides, a single entry with the id `menu`. */
const guideMenu = defineCollection({
  loader: glob({ base, pattern: 'README.md', generateId: () => 'menu' }),
});

/** The content collections of the site: the guides and their menu. */
export const collections = { guides, guideMenu };
