# impire.io

The launch page of Impire, served at `impire.io` and `www.impire.io` by GitHub Pages.

It is one static page: `index.html`, hand-written HTML and CSS with a small inline script that draws the cloud. There is no framework and no build step. `404.html` answers every other path; `CNAME` names the domain; `robots.txt` admits crawlers.

The page is the static twin of the console's front page, the signed-out site. The two change together: a change to the front page's words in `impire-console` (`src/surfaces/site/words.ts`) is a change to this page in the same work, and a sentence that leaves the front page leaves this page too. What the page is and why is in [`SPEC.md`](SPEC.md).

The workflow in `.github/workflows/pages.yml` checks the page on every pull request and, on `main`, publishes `index.html`, `404.html`, `robots.txt` and `CNAME` and nothing else.

The page embeds Selawik Regular and Semibold (Microsoft's open twin of Segoe UI, the brand's typeface; the console's own files, unhinted) and the latin subset of Cascadia Mono (fontsource 5.3.0), both under the SIL Open Font License 1.1; the look is the brand manual's (impire-hq `00-META/brand.md`, decision 0178): the cover and the close on navy, the content on white.
