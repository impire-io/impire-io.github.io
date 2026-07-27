# impire.io

The website for the impire constellation: a home page and three sub-sites
(pra, soulstream, imps).

## How it's built

By hand. HTML pages sharing one stylesheet, no framework, no external
requests (no webfonts, no analytics, no CDN). Deploy by copying the
directory to any static host — nothing needs to run.

```
index.html              the constellation (home)
assets/site.css         shared design system
pra/index.html          sub-site: PRA
pra/how-it-works.html   PRA's interactive explainer (self-contained, from the pra repo)
pra/book/               the PRA book, published as a draft (generated, see below)
soulstream/index.html   sub-site: soulstream
imps/index.html         sub-site: imps
tools/build-book.py     regenerates pra/book/ from the pra repo's book/ markdown
```

The one exception to "by hand" is `pra/book/`: a contents page, twelve
chapter pages, and a glossary, generated from `../pra/book/*.md` by
`tools/build-book.py` (stdlib Python, run it whenever the book changes).
The script keeps the chapter text verbatim — it asserts the visible text
of every generated page matches the markdown — and stamps each page with
a draft notice. The book is published as a draft on purpose: the pra
repo's own rule (journey episode 0047) is that no empirical claim is
final before a numbers audit re-verifies it, and that audit hasn't run
yet. The draft labels come off when it has.

## Deploying, and the WIP preview

Production is GitHub Pages: pushing `main` publishes to impire.io.
Nothing goes live until you push.

The work-in-progress site lives behind a login on Vercel (project
`impire-wip`, no custom domain — impire.io never points there). From
this directory:

```
vercel deploy
```

uploads the working tree as-is — committed or not — and prints a
`*.vercel.app` URL that only the project owner's Vercel login can open
(unauthenticated visitors are redirected to Vercel SSO; this is the
project's default "Standard Protection", don't turn it off). To show a
WIP state to someone else, use a shareable link from the deployment's
page on vercel.com — time-limited, no account needed on their end.

Two free-plan traps, learned the hard way:

- Production deployments are NOT behind the login (Vercel Authentication
  doesn't cover production on this plan), so **never `vercel deploy
  --prod` here**. The project's production slot deliberately holds a
  one-line placeholder — impire-wip.vercel.app says "nothing public
  here" — because a project's *first* deployment is auto-assigned to
  production whether you asked or not. If the project is ever recreated,
  deploy a placeholder first, the site second.
- Plain `vercel deploy` (a preview) is the protected one. Vercel's
  review system can hold a fresh deployment in a BLOCKED state that the
  CLI shows as endless "Building…" — check the Inspect URL on
  vercel.com if a deploy seems stuck.

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
be refreshed from there when the explainer changes. `pra/book/` is
generated from `../pra/book/` and should be regenerated
(`python3 tools/build-book.py`) when a chapter changes.
