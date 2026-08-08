// @ts-check
import { defineConfig } from 'astro/config';

// build.format 'file' is load-bearing: it reproduces the legacy URL space
// (flat /pra/book/NN-slug.html chapter files) exactly — GitHub Pages cannot
// serve redirects, so every pre-migration URL must keep resolving.
export default defineConfig({
  site: 'https://impire.io',
  build: { format: 'file' },
});
