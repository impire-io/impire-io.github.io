// The soulsystem — single source of truth for the map, the story, the
// reference legend, llms.txt, and structured data. Geometry is in the map's
// viewBox units; the SVG, the focus transforms, and the gather lines all
// render from this module so they can never drift apart.

export interface Body {
  id: string;
  name: string;
  role: string;
  cx: number;
  cy: number;
  coreR: number;
  haloR: number;
  label: { x: number; y: number; anchor: 'start' | 'middle' | 'end' };
  /** zoom applied when this body is the focused scroll step */
  zoom: number;
  /** optional focus point override (soulnode frames the whole system) */
  focus?: { x: number; y: number };
  hue: string; // CSS custom property name, deep/text-safe
  status: string;
  version: string;
  repo: string;
  /** one-line description, from soul-hq/00-GENESIS/vision.md */
  oneLiner: string;
}

export const VIEW = { w: 900, h: 560, cx: 450, cy: 280 };

export const ORBITS = [
  { rx: 150, ry: 92 },
  { rx: 255, ry: 156 },
  { rx: 360, ry: 220 },
];

export const BODIES: Body[] = [
  {
    id: 'soulstream',
    name: 'soulstream-core',
    role: 'the record',
    cx: 430, cy: 280, coreR: 10, haloR: 52,
    label: { x: 430, y: 322, anchor: 'middle' },
    zoom: 1.9,
    hue: 'soulstream',
    status: 'shipping',
    version: 'v0.8.4',
    repo: 'https://github.com/impire-io/soulstream-core',
    oneLiner:
      'The protocol and its reference library: topics as shared workbenches, operations, baselines, personas — collaboration as an op-log over NATS.',
  },
  {
    id: 'soulidentity',
    name: 'soulstream-identity',
    role: 'the name',
    cx: 294, cy: 188, coreR: 6, haloR: 30,
    label: { x: 266, y: 184, anchor: 'end' },
    zoom: 2.2,
    hue: 'soulidentity',
    status: 'identity plane',
    version: 'v0.2.0',
    repo: 'https://github.com/impire-io/soulstream-identity',
    oneLiner:
      'The identity plane: the home of the persona — vault-held keys, signing oracle, credential minting; signs and mints instead of handing out keys.',
  },
  {
    id: 'soulrealm',
    name: 'soulstream-workloads',
    role: 'the room',
    cx: 663, cy: 216, coreR: 6.5, haloR: 30,
    label: { x: 695, y: 212, anchor: 'start' },
    zoom: 2.2,
    hue: 'soulrealm',
    status: 'three backends · wrap',
    version: 'v0.3.0',
    repo: 'https://github.com/impire-io/soulstream-workloads',
    oneLiner:
      "The runtime: launches, supervises, observes, and retires a realm's agents and tools as workloads; everything worth keeping flows back to the record.",
  },
  {
    id: 'soulfold',
    name: 'soulstream-idp',
    role: 'the door',
    cx: 221, cy: 372, coreR: 6, haloR: 30,
    label: { x: 189, y: 368, anchor: 'end' },
    zoom: 2.2,
    hue: 'soulfold',
    status: 'passkeys · console',
    version: 'v0.4.1',
    repo: 'https://github.com/impire-io/soulstream-idp',
    oneLiner:
      'The default IAM: a self-hosted, passkey-first OIDC provider — who exists and who belongs — standing exactly where Entra or any OIDC provider may stand instead.',
  },
  {
    id: 'soulnode',
    name: 'soulstream',
    role: 'the house',
    cx: 706, cy: 446, coreR: 8, haloR: 38,
    label: { x: 742, y: 442, anchor: 'start' },
    zoom: 1.35,
    // frame the house with the rest of the system still in view
    focus: { x: 590, y: 375 },
    hue: 'soulnode',
    status: 'pre-release binaries',
    version: 'v0.11.0-rc.2',
    repo: 'https://github.com/impire-io/soulstream',
    oneLiner:
      'The single-binary distribution: the whole stack on a machine you own — soulstream init && soulstream up, point a client at the printed URL.',
  },
];

/** translate–scale–translate sandwich mapping the focus point to the viewBox
    center at the body's zoom; avoids transform-origin/transform-box, which
    are inconsistent for SVG across engines. */
export function focusTransform(body: Body): string {
  const fx = body.focus?.x ?? body.cx;
  const fy = body.focus?.y ?? body.cy;
  return `translate(${VIEW.cx}px, ${VIEW.cy}px) scale(${body.zoom}) translate(${-fx}px, ${-fy}px)`;
}
