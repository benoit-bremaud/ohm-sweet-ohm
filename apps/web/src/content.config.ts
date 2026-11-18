import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';

// The troubleshooting guides are read in place from the repository's troubleshooting/ folder
// (epic #79): GitHub and the site render the same files, nothing is copied.
const base = '../../troubleshooting';

/** One entry per guide, its id the guide folder (`10_resistance`). */
const guides = defineCollection({
  loader: glob({
    base,
    pattern: '[0-9][0-9]_*/README.md',
    generateId: ({ entry }) => entry.split('/')[0] ?? entry,
  }),
});

/** The menu of the guides, a single entry with the id `menu`. */
const guideMenu = defineCollection({
  loader: glob({ base, pattern: 'README.md', generateId: () => 'menu' }),
});

export const collections = { guides, guideMenu };
