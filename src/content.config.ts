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

// The PRA book, vendored verbatim from ../pra/book by tools/sync-book.py.
// Bodies are the upstream markdown untouched; frontmatter carries the chrome.
const book = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/book' }),
  schema: z.object({
    order: z.number(),
    num: z.string(),
    title: z.string(),
    part: z.string(),
    src: z.string(),
    kind: z.enum(['chapter', 'glossary']),
  }),
});

export const collections = { story, book };
