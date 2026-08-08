#!/usr/bin/env python3
"""Parity + link gate over the built site.

Usage: python3 tools/check-site.py dist

Asserts (1) every URL the pre-Astro site served still resolves to a file in
dist — GitHub Pages cannot redirect, so these paths are contractual — and
(2) every internal href/src in the built HTML resolves to a built file.
"""

import re
import sys
from pathlib import Path

# the complete URL space of the hand-written site (21 paths), frozen
LEGACY = [
    "/",
    "/soulsystem/",
    "/soulstream/",
    "/imps/",
    "/pra/",
    "/pra/how-it-works.html",
    "/pra/book/index.html",
    "/pra/book/01-the-frozen-brain.html",
    "/pra/book/02-forget-everything-or-remember-everything.html",
    "/pra/book/03-the-question-nobody-answers.html",
    "/pra/book/04-before-action-after.html",
    "/pra/book/05-not-words-not-pictures.html",
    "/pra/book/06-a-head-full-of-rival-guessers.html",
    "/pra/book/07-never-let-it-grade-its-own-homework.html",
    "/pra/book/08-the-price-of-a-dimension.html",
    "/pra/book/09-wanting-things.html",
    "/pra/book/10-the-brain-that-almost-stopped-learning-anyway.html",
    "/pra/book/11-no-scrapbook-required.html",
    "/pra/book/12-watching-it-learn.html",
    "/pra/book/glossary.html",
]


def resolve(dist: Path, path: str) -> Path:
    path = path.split("#", 1)[0].split("?", 1)[0]
    if path.endswith("/") or path == "":
        return dist / path.lstrip("/") / "index.html"
    p = dist / path.lstrip("/")
    if p.suffix:
        return p
    # extensionless: GitHub Pages serves either name.html or name/index.html
    if (dist / (path.lstrip("/") + ".html")).exists():
        return dist / (path.lstrip("/") + ".html")
    return p / "index.html"


def main() -> int:
    dist = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    if not dist.is_dir():
        print(f"check-site: no such directory {dist}", file=sys.stderr)
        return 2

    bad = 0
    for path in LEGACY:
        if not resolve(dist, path).is_file():
            print(f"check-site: LEGACY URL BROKEN {path}", file=sys.stderr)
            bad += 1

    ref = re.compile(r'(?:href|src)="([^"]+)"')
    for html in dist.rglob("*.html"):
        for target in ref.findall(html.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "mailto:", "#", "data:")):
                continue
            base = "/" + str(html.parent.relative_to(dist)) + "/" if html.parent != dist else "/"
            path = target if target.startswith("/") else base + target
            # normalize ./ and ../
            parts: list[str] = []
            for seg in path.split("/"):
                if seg in ("", "."):
                    continue
                if seg == "..":
                    parts and parts.pop()
                else:
                    parts.append(seg)
            norm = "/" + "/".join(parts) + ("/" if path.endswith("/") else "")
            if not resolve(dist, norm).is_file():
                print(f"check-site: broken link {target} in {html.relative_to(dist)}", file=sys.stderr)
                bad += 1

    if bad:
        print(f"check-site: {bad} problem(s)", file=sys.stderr)
        return 1
    print(f"check-site: OK — {len(LEGACY)} legacy URLs + all internal links resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
