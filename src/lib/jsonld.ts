// JSON-LD graph builders. Rule: nodes state only what the visible page text
// states — no hidden claims, no FAQPage. License URL points at the site's
// fair-code explanation page, which links the authoritative texts.

const SITE = 'https://impire.io';
export const LICENSE_URL = `${SITE}/license/`;

export const organization = () => ({
  '@type': 'Organization',
  '@id': `${SITE}/#org`,
  name: 'Impire',
  url: SITE,
  logo: `${SITE}/favicon.svg`,
  sameAs: ['https://github.com/impire-io'],
});

export const webSite = () => ({
  '@type': 'WebSite',
  '@id': `${SITE}/#site`,
  name: 'impire.io',
  url: SITE,
  publisher: { '@id': `${SITE}/#org` },
});

export const software = (opts: { name: string; description: string; repo: string; version?: string }) => ({
  '@type': 'SoftwareSourceCode',
  name: opts.name,
  description: opts.description,
  codeRepository: opts.repo,
  license: LICENSE_URL,
  ...(opts.version ? { version: opts.version } : {}),
  isPartOf: { '@id': `${SITE}/#site` },
});

export const article = (opts: { headline: string; description: string; url: string }) => ({
  '@type': 'Article',
  headline: opts.headline,
  description: opts.description,
  url: opts.url,
  author: { '@type': 'Person', name: 'Daan Gerits' },
  publisher: { '@id': `${SITE}/#org` },
  isPartOf: { '@id': `${SITE}/#site` },
});

/** assemble the page's single @graph script payload */
export const graph = (...nodes: object[]) => ({
  '@context': 'https://schema.org',
  '@graph': [organization(), webSite(), ...nodes],
});
