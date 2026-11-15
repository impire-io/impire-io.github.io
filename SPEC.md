# The launch page at the apex

**Decision:** impire-hq [`03-DECISIONS/0153-dev-is-reached-over-the-tailnet-alone-until-launch-and-the-apex-serves-the-launch-page-from-the-pages-repository.md`](https://github.com/impire-io/impire-hq/blob/main/03-DECISIONS/0153-dev-is-reached-over-the-tailnet-alone-until-launch-and-the-apex-serves-the-launch-page-from-the-pages-repository.md) § 3 and § 4.
**Design:** impire-hq [`02-DESIGN/03-console/03-the-signed-out-site.md`](https://github.com/impire-io/impire-hq/blob/main/02-DESIGN/03-console/03-the-signed-out-site.md) § the launch page at the apex, with § the page, in order; § widths; § for keyboard and screen reader; § the look; § where the words come from; § what this does not do.
**Work ID:** `0153-tailnet-dev-and-launch-page`.

## What it is

The console's front page as one static page: the top line, the opening with the drawn cloud, the statement, the four positions, *Already there when you connect.*, the close with *Decide once.*, and the footer, in that order, with the words of impire-console `src/surfaces/site/words.ts` and the look of its `src/ui/tokens.css` and `src/surfaces/site/site.css`. The cloud is the console's seeded drawing on a canvas; the constellations and the substrate are its seeded drawings, pre-rendered as inline SVG.

## Where it differs from the console's page

Each difference is the decision's, because no install stands behind the apex:

- *Request access* is a mail link to `hello@impire.io`: in the top line, in the opening, and in the close where the console's page has the sign-in card. There is no request form.
- There is no sign-in: no *Sign in*, no *Get started*, no *Sign in to your workspace*, no card, and the footer carries no *Sign in*. The close's paragraph keeps its first sentence and drops *Sign in with the account you already have; the first sign-in creates your workspace.*, which has nothing to point at here.
- The page is pre-rendered: it reads no platform profile.

## What it does not do

No tracking, no analytics, no third-party script, font, image or player, no cookie, nothing written to the browser's storage. A Content-Security-Policy in the page refuses anything loaded from elsewhere; the fonts are embedded. No claim the records do not back, no superlative, no comparison, no refusal. No path but `/`: everything else is `404.html`. Light only.
