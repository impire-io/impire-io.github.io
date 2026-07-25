# impire.io

The website for the impire constellation: a home page and three sub-sites
(pra, soulstream, imps).

## How it's built

By hand. Four HTML pages sharing one stylesheet, no framework, no build
step, no external requests (no webfonts, no analytics, no CDN). Deploy by
copying the directory to any static host.

```
index.html              the constellation (home)
assets/site.css         shared design system
pra/index.html          sub-site: PRA
pra/how-it-works.html   PRA's interactive explainer (self-contained, from the pra repo)
soulstream/index.html   sub-site: soulstream
imps/index.html         sub-site: imps
```

## Design system

One dark world, three hues. Tokens descend from `pra/explainer/index.html`
(the first shipped piece of the visual language). Each sub-site sets
`data-p` on `<body>`, which selects its accent through `--a`; everything
else derives from the shared tokens. Each hero carries a small ambient
canvas in the project's hue: rival maps for pra, braiding streams for
soulstream, sparks and one flame for imps.
All motion respects `prefers-reduced-motion`.

## Copy

The copy contract is `pra/book/STYLE.md` in the pra repository: write from
the specific, no hype, and every page says plainly what does not work or
exist yet. PRA's page is `pra/website-copy.md` nearly verbatim; the other
two were written to the same shape and checked against the repos they
describe.

`pra/how-it-works.html` is a copy of `pra/explainer/index.html` and should
be refreshed from there when the explainer changes.
