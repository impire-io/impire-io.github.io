#!/usr/bin/env python3
"""Vendor the PRA book markdown into the site's content collection.

Usage: python3 tools/sync-book.py [path-to-pra-book]

The book's source of truth stays ../pra/book in the impire workspace; this
script copies each chapter (and the glossary) into src/content/book/ with
frontmatter, bodies verbatim. The vendored copies are committed, so CI never
needs the sibling repository. Run it whenever the book changes upstream.

Verbatim means verbatim: the body written is byte-identical to the source
minus the leading provenance comment and H1 (both moved to frontmatter);
the script re-reads what it wrote and asserts exactly that.
"""

import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
DEFAULT_SRC = SITE.parent / "pra" / "book"
OUT = SITE / "src" / "content" / "book"


def parse_md(path):
    """Split a book markdown file into (provenance comment, H1 title, body)."""
    lines = path.read_text(encoding="utf-8").splitlines()
    i = 0
    comment = []
    if lines and lines[0].startswith("<!--"):
        while i < len(lines):
            comment.append(lines[i])
            i += 1
            if "-->" in comment[-1]:
                break
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i == len(lines) or not lines[i].startswith("# "):
        raise SystemExit(f"{path.name}: no H1 title found")
    title = lines[i][2:].strip()
    body = "\n".join(lines[i + 1:]).strip("\n") + "\n"
    return "\n".join(comment), title, body


def part_title(dirname):
    m = re.match(r"part-(\d+)-(.+)", dirname)
    words = m.group(2).replace("-", " ")
    return f"Part {m.group(1)} — {words[0].upper()}{words[1:]}"


def yaml_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def write_entry(out_name, meta, body):
    front = "\n".join(f"{k}: {yaml_str(v) if isinstance(v, str) else v}" for k, v in meta.items())
    text = f"---\n{front}\n---\n{body}"
    out = OUT / out_name
    out.write_text(text, encoding="utf-8")
    # the whole point of vendoring: what landed is what the source says
    reread = out.read_text(encoding="utf-8").split("---\n", 2)[2]
    if reread != body:
        raise SystemExit(f"{out_name}: vendored body diverged from source")


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SRC
    if not src.is_dir():
        raise SystemExit(f"book source not found: {src}")
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.md"):
        old.unlink()

    order = 0
    for part_dir in sorted(src.glob("part-*")):
        for md in sorted(part_dir.glob("*.md")):
            order += 1
            prov, title, body = parse_md(md)
            write_entry(md.name, {
                "order": order,
                "num": md.name[:2],
                "title": title,
                "part": part_title(part_dir.name),
                "src": f"{part_dir.name}/{md.name}",
                "kind": "chapter",
            }, body)

    prov, g_title, g_body = parse_md(src / "GLOSSARY.md")
    write_entry("glossary.md", {
        "order": order + 1,
        "num": "··",
        "title": g_title,
        "part": "Reference",
        "src": "GLOSSARY.md",
        "kind": "glossary",
    }, g_body)

    print(f"vendored {order} chapters + glossary into {OUT.relative_to(SITE)}")


if __name__ == "__main__":
    main()
