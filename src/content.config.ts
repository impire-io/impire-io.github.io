import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

// The homepage scroll story. One file per step; the SoulStory component and
// the page's markdown mirror both render these bodies, so the interactive
// page and the agent-readable text can never drift apart.
const story = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/story' }),
  schema: z.object({
    order: z.number(),
    /** matches a body id from src/data/soulsystem.ts, or 'overview' | 'all' */
    step: z.string(),
    title: z.string(),
    /** mono eyebrow above the step heading */
    eyebrow: z.string(),
  }),
});

export const collections = { story };
