// @ts-check
import { defineConfig } from 'astro/config';

// build.format 'preserve' is load-bearing: it mirrors the source structure
// exactly — index.astro stays a directory index (/soulsystem/), named files
// stay flat .html (/pra/book/01-the-frozen-brain.html). GitHub Pages cannot
// serve redirects, so every pre-migration URL must keep resolving.
export default defineConfig({
  site: 'https://impire.io',
  build: { format: 'preserve' },
  // the book is vendored verbatim and checked for text fidelity against its
  // source — no typographic rewriting
  markdown: { smartypants: false },
});
