#!/usr/bin/env python3
"""Build the PRA book pages (pra/book/*.html) from the pra repository's
book/ markdown.

Usage: python3 tools/build-book.py [path-to-pra-book]

The book's source of truth is ../pra/book in the impire workspace. This
script converts the chapter markdown verbatim into the site's chrome and
asserts, per chapter, that the visible text of the generated page matches
the markdown. Deploying the site still needs no build step; this only
refreshes the generated pages when the book changes.

The markdown subset the chapters use (checked, not assumed): one H1, H2
sections, paragraphs, `> **Under the hood: ...**` asides, fenced code
blocks, inline code/bold/italic, and one provenance HTML comment at the
top of each file. Anything else fails loudly.
"""

import html as htmllib
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
DEFAULT_SRC = SITE.parent / "pra" / "book"
OUT = SITE / "pra" / "book"

GITHUB_BOOK = "https://github.com/impire-io/poseres/blob/main/book"

DRAFT_NOTE = (
    '<p class="book-draftnote">draft · the numbers audit has not run yet — '
    '<a href="./#draft">read measured numbers as provisional</a></p>'
)


# ---------------------------------------------------------------- inline

def inline(text):
    """Escape HTML, then apply the chapters' inline markup: `code`,
    **bold**, *italic*. Code spans are protected from emphasis rules."""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    out = []
    for part in re.split(r"(`[^`]+`)", text):
        if len(part) > 2 and part.startswith("`") and part.endswith("`"):
            out.append("<code>" + part[1:-1] + "</code>")
        else:
            part = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", part, flags=re.S)
            part = re.sub(r"\*(.+?)\*", r"<em>\1</em>", part, flags=re.S)
            out.append(part)
    joined = "".join(out)
    if "*" in re.sub(r"<code>.*?</code>", "", joined, flags=re.S):
        raise SystemExit(f"unbalanced emphasis marker in: {text[:80]!r}")
    return joined


# ---------------------------------------------------------------- blocks

def aside_html(content_lines):
    """One `> **Under the hood: ...**` box. Content may hold several
    paragraphs, separated by empty quote lines."""
    paras, cur = [], []
    for line in content_lines:
        if line.strip():
            cur.append(line)
        elif cur:
            paras.append("\n".join(cur))
            cur = []
    if cur:
        paras.append("\n".join(cur))

    m = re.match(r"\*\*(Under the hood:.+?)\*\*\s*(.*)", paras[0], flags=re.S)
    if not m:
        raise SystemExit(f"blockquote without Under-the-hood label: {paras[0][:80]!r}")
    label, rest = m.group(1), m.group(2)
    body = [f'<p class="uth-label">{inline(label)}</p>']
    for p in ([rest] if rest else []) + paras[1:]:
        body.append(f"<p>{inline(p)}</p>")
    return '<aside class="uth">\n' + "\n".join(body) + "\n</aside>"


def blocks_to_html(lines):
    """Convert a chapter body (markdown lines, no H1) to HTML blocks."""
    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
        elif line.startswith("```"):
            j = i + 1
            code = []
            while j < len(lines) and not lines[j].startswith("```"):
                code.append(lines[j])
                j += 1
            if j == len(lines):
                raise SystemExit("unclosed code fence")
            escaped = "\n".join(code).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            blocks.append(f"<pre><code>{escaped}</code></pre>")
            i = j + 1
        elif line.startswith("## "):
            blocks.append(f"<h2>{inline(line[3:])}</h2>")
            i += 1
        elif line.startswith("#"):
            raise SystemExit(f"unexpected heading level: {line!r}")
        elif line.startswith(">"):
            quote = []
            while i < len(lines) and lines[i].startswith(">"):
                quote.append(lines[i][2:] if lines[i].startswith("> ") else lines[i][1:])
                i += 1
            blocks.append(aside_html(quote))
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not lines[i].startswith(("#", ">", "```")):
                para.append(lines[i])
                i += 1
            blocks.append(f"<p>{inline(chr(10).join(para))}</p>")
    return "\n\n".join(blocks)


# ---------------------------------------------------------------- fidelity

def _normalize(text):
    """Reduce either markdown or tag-stripped HTML to comparable text:
    drop structural markers and collapse whitespace."""
    text = re.sub(r"(?m)^\s*(>|#{1,6}) ?", "", text)
    for token in ("```", "**", "*", "`"):
        text = text.replace(token, "")
    return re.sub(r"\s+", " ", text).strip()


def check_fidelity(md_body, article_html, name):
    visible = re.sub(r"<!--.*?-->", " ", article_html, flags=re.S)
    # inline tags vanish without a trace (<em>x</em>. must stay "x.");
    # block boundaries already carry newlines outside the tags
    visible = re.sub(r"<[^>]+>", "", visible)
    visible = htmllib.unescape(visible)
    want, got = _normalize(md_body), _normalize(visible)
    if want != got:
        for k in range(min(len(want), len(got))):
            if want[k] != got[k]:
                raise SystemExit(
                    f"{name}: text diverges from source near …{want[max(0, k - 60):k + 60]!r}"
                )
        raise SystemExit(f"{name}: generated text length differs from source")


# ---------------------------------------------------------------- parsing

def parse_md(path):
    """Split a book markdown file into (provenance comment, H1 title, body lines)."""
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
    return "\n".join(comment), title, lines[i + 1:]


def part_title(dirname):
    m = re.match(r"part-(\d+)-(.+)", dirname)
    words = m.group(2).replace("-", " ")
    return f"Part {m.group(1)} — {words[0].upper()}{words[1:]}"


# ---------------------------------------------------------------- chrome

def page(*, title, description, body, source_line, prov=""):
    """Shared chrome for every generated page (depth: /pra/book/)."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{description}">
<title>{title}</title>
<link rel="stylesheet" href="../../assets/site.css">
</head>
{prov and prov + chr(10)}<body data-p="pra">

<nav class="nav" aria-label="impire projects">
  <a class="wordmark" href="../../"><b>impire</b><span class="tld">.io</span>
    <span class="dots" aria-hidden="true">
      <i style="background:var(--pra)"></i><i style="background:var(--soulstream)"></i><i style="background:var(--imps)"></i>
    </span>
  </a>
  <span class="links">
    <a href="../" data-p="pra" aria-current="page">pra</a>
    <a href="../../soulstream/" data-p="soulstream">soulstream</a>
    <a href="../../imps/" data-p="imps">imps</a>
  </span>
</nav>

<main class="book">
{body}
</main>

<footer>
  <div class="cols">
    <div>
      <p>{source_line}</p>
      <p><a href="../">← pra</a> · <a href="./">book contents</a></p>
    </div>
    <div class="meta">
      <span>impire.io/pra · no cookies, no tracking</span>
    </div>
  </div>
</footer>

</body>
</html>
"""


def pager(prev_entry, next_entry):
    parts = []
    if prev_entry:
        href, label = prev_entry
        parts.append(
            f'<a class="prev" href="{href}"><span>previous</span>{label}</a>'
        )
    if next_entry:
        href, label = next_entry
        parts.append(
            f'<a class="next" href="{href}"><span>next</span>{label}</a>'
        )
    return '<nav class="book-pager" aria-label="book pages">\n' + "\n".join(parts) + "\n</nav>"


# ---------------------------------------------------------------- build

def build(src):
    OUT.mkdir(parents=True, exist_ok=True)

    parts = []
    for part_dir in sorted(src.glob("part-*")):
        chapters = []
        for md in sorted(part_dir.glob("*.md")):
            prov, title, body = parse_md(md)
            chapters.append({
                "num": md.name[:2],
                "slug": md.stem,
                "title": title,
                "prov": prov,
                "body": body,
                "src": f"{part_dir.name}/{md.name}",
                "part": part_title(part_dir.name),
            })
        parts.append((part_title(part_dir.name), chapters))

    flat = [ch for _, chapters in parts for ch in chapters]

    # reading order: chapters, then the glossary
    order = [(f"./{ch['slug']}.html", f"{ch['num']} · {ch['title']}") for ch in flat]
    order.append(("./glossary.html", "Glossary"))

    for idx, ch in enumerate(flat):
        article = blocks_to_html(ch["body"])
        check_fidelity("\n".join(ch["body"]), article, ch["src"])
        head = f"""<header class="book-head">
  <p class="eyebrow"><a href="./">the pra book</a> · {ch["part"].lower()}</p>
  <p class="book-part">chapter {ch["num"]} of {len(flat)}</p>
  <h1>{inline(ch["title"])}</h1>
  {DRAFT_NOTE}
</header>"""
        body = f"""{head}

<article class="book-prose">
{article}
</article>

{pager(order[idx - 1] if idx else None, order[idx + 1])}"""
        out = OUT / f"{ch['slug']}.html"
        out.write_text(page(
            title=f"{ch['num']} · {ch['title']} — the PRA book",
            description=f"Chapter {ch['num']} of the PRA book, published as a draft: {ch['title']}.",
            body=body,
            source_line=(
                'A chapter of the PRA book, published as a draft. Its source is '
                f'<a href="{GITHUB_BOOK}/{ch["src"]}">book/{ch["src"]}</a> in the PRA repository.'
            ),
            prov=ch["prov"],
        ), encoding="utf-8")

    # glossary
    prov, g_title, g_body = parse_md(src / "GLOSSARY.md")
    g_article = blocks_to_html(g_body)
    check_fidelity("\n".join(g_body), g_article, "GLOSSARY.md")
    body = f"""<header class="book-head">
  <p class="eyebrow"><a href="./">the pra book</a> · reference</p>
  <h1>{inline(g_title)}</h1>
  {DRAFT_NOTE}
</header>

<article class="book-prose">
{g_article}
</article>

{pager(order[-2], None)}"""
    (OUT / "glossary.html").write_text(page(
        title="Glossary — the PRA book",
        description="Every plain-words definition from the PRA book, in order of appearance.",
        body=body,
        source_line=(
            'The glossary of the PRA book, published as a draft. Its source is '
            f'<a href="{GITHUB_BOOK}/GLOSSARY.md">book/GLOSSARY.md</a> in the PRA repository.'
        ),
    ), encoding="utf-8")

    # contents page
    toc = []
    for title, chapters in parts:
        items = "\n".join(
            f'    <li><a href="./{ch["slug"]}.html">'
            f'<span class="n">{ch["num"]}</span>{htmllib.escape(ch["title"])}</a></li>'
            for ch in chapters
        )
        toc.append(f"""  <section>
  <h2>{title}</h2>
  <ol>
{items}
  </ol>
  </section>""")
    toc.append("""  <section>
  <h2>Part 5 — Teachers</h2>
  <p class="note">Not written yet, on purpose. Its one measured foundation is that
  several worlds can already feed one brain safely; the rest waits on results
  the project doesn't have.</p>
  </section>""")
    toc.append("""  <section>
  <h2>Reference</h2>
  <ol>
    <li><a href="./glossary.html"><span class="n">·</span>Glossary — every plain-words definition, in order of appearance</a></li>
  </ol>
  </section>""")
    toc_html = "\n".join(toc)

    body = f"""<header class="book-head">
  <p class="eyebrow"><a href="../">pra</a> · the book · draft</p>
  <h1>The PRA book</h1>
  <p class="book-lede">
    A book about the Pose Resolution Architecture: why frozen models fail, what a
    sensorimotor triplet is, and how a population of competing frames learns
    structure nobody specified.
  </p>
  <p class="book-lede">
    It's written in first person by one builder, and the reversals are the plot:
    nearly every chapter holds a belief that a measurement later refuted. Each
    chapter also carries fenced <em>Under the hood</em> boxes for engineers;
    skipping every box loses precision, never the story.
  </p>
</header>

<section class="book-draft" id="draft">
  <h2>Published as a draft</h2>
  <p>
    These chapters are written, but the book's own rule is that no empirical claim
    ships as final before a numbers audit re-verifies it against the repository,
    and that audit hasn't run yet. Read the story now; read the measured numbers
    as provisional until the pages say otherwise.
  </p>
</section>

<nav class="book-toc" aria-label="contents">
{toc_html}
</nav>"""

    (OUT / "index.html").write_text(page(
        title="The PRA book — a draft, published as one",
        description="The PRA book: why frozen models fail, what a sensorimotor triplet is, and how a population of competing frames learns structure nobody specified. Published as a draft.",
        body=body,
        source_line=(
            'The PRA book is written in the open. Its source lives in '
            f'<a href="{GITHUB_BOOK}">book/</a> in the PRA repository, next to the '
            'measurements it describes.'
        ),
    ), encoding="utf-8")

    print(f"built {len(flat)} chapters + glossary + contents → {OUT}")


if __name__ == "__main__":
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SRC
    if not src.is_dir():
        raise SystemExit(f"book source not found: {src}")
    build(src)
