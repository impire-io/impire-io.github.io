#!/bin/sh
# Post-build gate for the agent-accessibility surface. Run after `npm run build`.
set -e
fail() { echo "verify-dist: FAIL — $1" >&2; exit 1; }

[ -f dist/llms.txt ] || fail "dist/llms.txt missing"
[ "$(wc -c < dist/llms.txt)" -lt 5120 ] || fail "llms.txt over 5KB"
head -1 dist/llms.txt | grep -q '^# impire.io$' || fail "llms.txt heading"
sed -n '3p' dist/llms.txt | grep -q '^>' || fail "llms.txt summary blockquote"

[ -f dist/llms-full.txt ] || fail "llms-full.txt missing"
[ -f dist/robots.txt ] || fail "robots.txt missing"
grep -q '^Sitemap: https://impire.io/sitemap.xml' dist/robots.txt || fail "robots Sitemap directive"

[ -f dist/sitemap.xml ] || fail "sitemap.xml missing"
# every sitemap loc must have both its page and its markdown mirror in dist
grep -o '<loc>[^<]*</loc>' dist/sitemap.xml | sed 's/<[^>]*>//g' | while read -r url; do
  path="${url#https://impire.io}"
  case "$path" in
    *.html) page="dist$path"; mirror="dist$(echo "$path" | sed 's/\.html$/.md/')" ;;
    *)      page="dist${path}index.html"; mirror="dist${path}index.md" ;;
  esac
  [ -f "$page" ] || fail "sitemap page missing: $page"
  [ -f "$mirror" ] || fail "markdown mirror missing: $mirror"
done

# every built page carries canonical, the mirror advert, og:image, and JSON-LD
find dist -name '*.html' ! -path 'dist/pra/how-it-works.html' | while read -r f; do
  grep -q 'rel="canonical"' "$f" || fail "no canonical in $f"
  grep -q 'rel="alternate" type="text/markdown"' "$f" || fail "no md alternate in $f"
  grep -q 'property="og:image"' "$f" || fail "no og:image in $f"
  grep -q 'application/ld+json' "$f" || fail "no JSON-LD in $f"
done

# JSON-LD blocks parse as JSON
node -e '
  const { readFileSync } = require("fs");
  const { execSync } = require("child_process");
  const files = execSync("find dist -name \"*.html\" ! -path \"dist/pra/how-it-works.html\"").toString().trim().split("\n");
  for (const f of files) {
    const html = readFileSync(f, "utf8");
    const m = html.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/);
    if (!m) continue;
    JSON.parse(m[1]);
  }
' || fail "invalid JSON-LD"

echo "verify-dist: OK"
