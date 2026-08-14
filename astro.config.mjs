// @ts-check
import { defineConfig } from 'astro/config';

// build.format 'preserve' is load-bearing: it mirrors the source structure
// exactly — index.astro stays a directory index (/soulsystem/). GitHub Pages
// cannot serve redirects, so every pre-migration URL must keep resolving;
// the flat .html ones (the explainer, the retired book's redirect stubs
// pointing at impire.io/poseres-book/) are served verbatim from public/.
export default defineConfig({
  site: 'https://impire.io',
  build: { format: 'preserve' },
  // prose is served exactly as written — no typographic rewriting
  markdown: { smartypants: false },
});
