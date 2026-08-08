# impire.io

The website: the soulsystem as the main story, with PRA and imps under the
research wing. Astro static build, one light theme, no external requests
except the GoatCounter beacon (and only in production).

## Build

```
npm ci
npm run dev        # local dev server on :4321
npm run build      # dist/ = astro build + scripts/build-mirrors.mjs
```

The postbuild script derives, from the built HTML (so nothing can drift):
markdown mirrors for every page (`/<page>/index.md`, `/pra/book/<slug>.md`),
`/llms.txt`, `/llms-full.txt`, and `/sitemap.xml`.

Gates (both run in CI, both must be green):

```
python3 tools/check-site.py dist   # every pre-Astro URL still resolves + link check
sh scripts/verify-dist.sh          # llms.txt/mirrors/canonical/OG/JSON-LD surface
```

## The book

`src/content/book/` is vendored verbatim from the sibling `../pra/book` by

```
python3 tools/sync-book.py
```

Run it when the book changes upstream and commit the result; CI never needs
the pra repository. Chapter text fidelity is byte-checked (smartypants is off
for this reason). The interactive explainer ships verbatim at
`public/pra/how-it-works.html`; its source of truth is `../pra/explainer/`.

## Design system

Light only — "one light world, five hues" (`src/styles/tokens.css`): paper
with a violet cast, and per-project hue pairs. The deep hue is for text,
eyebrows, strokes, and focus rings (every value clears 4.5:1 on the paper);
the `-bright` partner is for fills, halos, and washes — never text. Display
type is Bricolage Grotesque (self-hosted via `@fontsource-variable`); body
stays on system stacks. Mono eyebrows are the brand carry-over from the dark
era.

The homepage scroll story lives in
`src/components/soulsystem/{SoulMap,SoulStory}.astro`, driven by
`src/data/soulsystem.ts` (geometry, hues, zooms, statuses — the single source
for the map, the story, and the reference legend). Step copy is
`src/content/story/*.md`. Everything degrades: no JS renders the full
document, reduced motion gets zero transforms.

## Deploy

**Production is GitHub Pages via Actions** (`.github/workflows/deploy.yml`):
push `main` → build → gates → deploy-pages. The custom domain (impire.io) and
HTTPS live in the repo's Pages settings — there is no CNAME file anymore.
Repo setting required once: *Settings → Pages → Source: GitHub Actions*.

**WIP preview is Vercel**, project `impire-wip`, behind Vercel's SSO:

```
vercel deploy      # never --prod: production isn't behind the login
```

Vercel auto-detects Astro; previews are attributed by the HEAD commit's
author email (this repo commits as daan.gerits@gmail.com, repo-local config).
Preview deployments send `X-Robots-Tag: noindex` on Vercel's side.

## Analytics

GoatCounter, guarded (`src/components/Analytics.astro`): only the
`impire.io` hostname loads the vendored `public/js/count.js`, DNT/GPC are
honored, and dev/preview/localhost make zero analytics requests. Events:
`ext-github-<repo>` outbound clicks and `soulsystem-story-completed`.
Dashboard: https://impire.goatcounter.com.

## License

Source-available under the Sustainable Use License (fair-code) — see
`LICENSE` and https://impire.io/license/.
