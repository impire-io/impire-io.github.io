#!/usr/bin/env node
// Postbuild agent-accessibility pass. Runs after `astro build` and derives,
// from the built HTML itself (so nothing can drift):
//   - a markdown mirror per page   (/<page>/index.md, /pra/book/<slug>.md)
//   - /llms.txt                    (curated index, links point at mirrors)
//   - /llms-full.txt               (the whole site's text in one fetch)
//   - /sitemap.xml                 (no lastmod — omitted rather than faked)
// The HTML→markdown converter understands exactly the tags this site emits;
// anything unexpected passes through as text, never breaking the build.

import { readFileSync, writeFileSync, existsSync, readdirSync } from 'node:fs';
import { join } from 'node:path';

const DIST = new URL('../dist/', import.meta.url).pathname;
const SITE = 'https://impire.io';

// section pages in reading order; book chapters are discovered from dist
const SECTIONS = [
  { path: '/', section: 'soulsystem' },
  { path: '/soulsystem/', section: 'soulsystem', repo: null },
  { path: '/soulstream/', section: 'soulsystem', repo: 'https://github.com/impire-io/soulstream' },
  { path: '/research/', section: 'research' },
  { path: '/pra/', section: 'research', repo: 'https://github.com/impire-io/poseres' },
  { path: '/imps/', section: 'research', repo: 'https://github.com/impire-io/imps' },
  { path: '/about/', section: 'meta' },
  { path: '/license/', section: 'meta' },
];

const ORBIT_REPOS = [
  ['soulidentity', 'the name — identity and signing for personas'],
  ['soulrealm', 'the room — where agents and tools run as workloads'],
  ['soulfold', 'the door — a self-hosted, passkey-first OIDC provider'],
  ['soulnode', 'the house — the whole stack as one binary'],
];

// ---------------------------------------------------------------- html → md

const unescapeHtml = (s) =>
  s
    .replaceAll('&lt;', '<')
    .replaceAll('&gt;', '>')
    .replaceAll('&quot;', '"')
    .replaceAll('&#39;', "'")
    .replaceAll('&amp;', '&');

function inlineMd(html, pagePath) {
  let s = html;
  s = s.replace(/<!--[\s\S]*?-->/g, '');
  s = s.replace(/<a\b[^>]*href="([^"]*)"[^>]*>([\s\S]*?)<\/a>/gi, (_, href, text) => {
    const abs = href.startsWith('http') ? href : new URL(href, SITE + pagePath).href;
    return `[${inlineMd(text, pagePath)}](${abs})`;
  });
  s = s.replace(/<(?:b|strong)\b[^>]*>([\s\S]*?)<\/(?:b|strong)>/gi, '**$1**');
  s = s.replace(/<(?:em|i)\b[^>]*>([\s\S]*?)<\/(?:em|i)>/gi, '*$1*');
  s = s.replace(/<code\b[^>]*>([\s\S]*?)<\/code>/gi, (_, t) => '`' + unescapeHtml(t) + '`');
  s = s.replace(/<[^>]+>/g, '');
  return unescapeHtml(s).replace(/\s+/g, ' ').trim();
}

function htmlToMd(html, pagePath) {
  const out = [];
  // svg maps become their accessible description
  html = html.replace(/<svg\b[^>]*aria-label="([^"]*)"[^>]*>[\s\S]*?<\/svg>/gi, (_, label) => `<p><em>[diagram: ${label}]</em></p>`);
  html = html.replace(/<svg\b[^>]*>[\s\S]*?<\/svg>/gi, '');
  html = html.replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, '');
  html = html.replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi, '');

  const block = /<(h1|h2|h3|p|li|pre|figcaption)\b[^>]*>([\s\S]*?)<\/\1>/gi;
  let m;
  while ((m = block.exec(html)) !== null) {
    const [, tag, inner] = m;
    if (tag === 'pre') {
      const code = unescapeHtml(inner.replace(/<[^>]+>/g, ''));
      out.push('```\n' + code + '\n```');
      continue;
    }
    // skip blocks nested inside a pre we already emitted
    const text = inlineMd(inner, pagePath);
    if (!text) continue;
    if (tag === 'h1') out.push(`# ${text}`);
    else if (tag === 'h2') out.push(`## ${text}`);
    else if (tag === 'h3') out.push(`### ${text}`);
    else if (tag === 'li') out.push(`- ${text}`);
    else out.push(text);
  }
  return out.join('\n\n');
}

// ---------------------------------------------------------------- helpers

const distFile = (path) =>
  path.endsWith('.html') ? join(DIST, path) : join(DIST, path, 'index.html');

const mirrorFile = (path) =>
  path.endsWith('.html') ? join(DIST, path.replace(/\.html$/, '.md')) : join(DIST, path, 'index.md');

const mirrorUrl = (path) =>
  path.endsWith('.html') ? SITE + path.replace(/\.html$/, '.md') : SITE + path + 'index.md';

function pageMeta(html) {
  const title = (html.match(/<title>([\s\S]*?)<\/title>/) ?? [])[1] ?? '';
  const description = (html.match(/<meta name="description" content="([^"]*)"/) ?? [])[1] ?? '';
  return { title: unescapeHtml(title.trim()), description: unescapeHtml(description) };
}

function contentOf(html) {
  // everything between the shared nav and the footer is page content
  const afterNav = html.split('</nav>').slice(1).join('</nav>');
  return afterNav.split(/<footer\b/)[0] ?? afterNav;
}

// ---------------------------------------------------------------- build

const pages = [...SECTIONS];
for (const f of readdirSync(join(DIST, 'pra', 'book')).sort()) {
  if (f.endsWith('.html') && f !== 'index.html') {
    pages.push({ path: `/pra/book/${f}`, section: 'book' });
  }
}
pages.splice(
  pages.findIndex((p) => p.section === 'book'),
  0,
  { path: '/pra/book/', section: 'book' },
);

const built = [];
for (const page of pages) {
  const file = distFile(page.path);
  if (!existsSync(file)) {
    console.error(`build-mirrors: missing ${file}`);
    process.exit(1);
  }
  const html = readFileSync(file, 'utf8');
  const { title, description } = pageMeta(html);
  const md = htmlToMd(contentOf(html), page.path);
  const body = `<!-- markdown mirror of ${SITE}${page.path} — generated from the built page; the canonical HTML lives at that URL -->\n\n${md}\n`;
  writeFileSync(mirrorFile(page.path), body);
  built.push({ ...page, title, description, mirror: mirrorUrl(page.path), body });
}

// llms.txt — curated, <5KB, links point at the mirrors
const by = (s) => built.filter((p) => p.section === s);
const line = (p) => `- [${p.title}](${p.mirror}): ${p.description}${p.repo ? ` (code: ${p.repo})` : ''}`;
const llms = `# impire.io

> Impire builds the soulsystem — five source-available (fair-code) components
> for human–AI collaboration around one signed record — plus open research
> into machines that learn by doing. All code: https://github.com/impire-io.
> License: free to use and self-host; commercial offering requires an
> agreement (${SITE}/license/).

Every page has a markdown mirror at <page-url>index.md (flat .html pages: same
name with .md). The whole site in one fetch: ${SITE}/llms-full.txt

## Soulsystem

${by('soulsystem').map(line).join('\n')}
${ORBIT_REPOS.map(([n, d]) => `- [${n} (code)](https://github.com/impire-io/${n}): ${d}`).join('\n')}

## Research

${by('research').map(line).join('\n')}

## The PRA book (draft)

${by('book')
  .map((p) => (p.path === '/pra/book/' ? line(p) : `- [${p.title.replace(' — the PRA book', '')}](${p.mirror})`))
  .join('\n')}

## Optional

- [Impire on GitHub](https://github.com/impire-io): every repository, fair-code licensed
- [soul-hq](https://github.com/impire-io/soul-hq): the ecosystem's vision, roadmap, and full decision journal
- [License](${SITE}/license/index.md): the Sustainable Use License, explained
`;
writeFileSync(join(DIST, 'llms.txt'), llms);

// llms-full.txt — the corpus, mirrors concatenated in reading order
const full = built
  .map((p) => `\n\n---\n\n<!-- ${SITE}${p.path} -->\n\n${p.body}`)
  .join('');
writeFileSync(join(DIST, 'llms-full.txt'), `# impire.io — full text\n${full}`);

// sitemap.xml — every page; no lastmod (omitted rather than faked)
const urls = built
  .map((p) => `  <url><loc>${SITE}${p.path}</loc></url>`)
  .join('\n');
writeFileSync(
  join(DIST, 'sitemap.xml'),
  `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls}\n</urlset>\n`,
);

const kb = (f) => (readFileSync(join(DIST, f)).length / 1024).toFixed(1);
console.log(
  `build-mirrors: ${built.length} mirrors, llms.txt ${kb('llms.txt')}KB, llms-full.txt ${kb('llms-full.txt')}KB, sitemap ${built.length} urls`,
);
