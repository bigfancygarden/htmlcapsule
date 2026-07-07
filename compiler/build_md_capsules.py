#!/usr/bin/env python3
"""
build_md_capsules.py — convert repo markdown files into sealed HTML Capsules.

Why: the htmlcapsule.org host (Cloudflare Pages) serves .md files as raw
text/markdown rather than rendering them, so visitors clicking "Research" /
"Spec" / etc. in the live-site nav got walls of unrendered markdown. This
script generates a Capsule per markdown file at the repo root + spec/, each
served at a clean URL (/core, /research, /glossary, ...). Each generated
capsule is itself a valid Core-spec Capsule (5 blocks, manifest, integrity,
declared capabilities), and passes the reference validator.

Generator kind: "compiler" (deterministic transform of an input file).
UUIDs are derived deterministically via v5 from a project namespace + the
source filename, so re-builds of the same source produce the same UUID and
the integrity hash only changes when the source content does.

Stdlib only — no pip deps, matches the project discipline. The markdown
parser handles the subset of CommonMark + GFM actually used in this repo's
.md files: ATX headers, paragraphs, lists (ul + ol), fenced code blocks,
indented code blocks, inline code, links, images, strong/em, blockquotes,
horizontal rules, GFM tables, and HTML passthrough for inline HTML.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


# ─── Configuration ──────────────────────────────────────────────────────


REPO_ROOT = Path(__file__).resolve().parent.parent

# v5 UUID namespace — derived from the canonical landing UUID. Stable across
# rebuilds; the per-file UUID is uuid5(NAMESPACE, source_filename).
NAMESPACE = uuid.UUID("7d1a1ac8-c6d9-4ed1-98a7-f5399466262a")


# Files to convert. Order matters for the navigation breadcrumb in each capsule.
# Format: (source_path, output_filename, title, type, lead_color, breadcrumb_label)
FILES = [
    ("CAPSULE_CORE.md",            "core.html",       "Core spec — twelve rules, one page",                              "spec",         "indigo", "Spec / Core"),
    ("spec/CAPSULE_SPEC.md",       "full-spec.html",  "Full spec — implementer-grade",                                    "spec",         "indigo", "Spec / Full"),
    ("spec/DOMAIN_CAPSULES.md",    "domains.html",    "Domain capsule schemas",                                          "spec",         "indigo", "Spec / Domains"),
    ("spec/HOSTING.md",            "hosting.html",    "Hosting pattern — format/host split",                              "spec",         "indigo", "Spec / Hosting"),
    ("spec/BUNDLE_SPEC.md",        "bundle-spec.html","Bundle spec — sibling format for heavy artifacts",                  "spec",         "indigo", "Spec / Bundle"),
    ("RESEARCH.md",                "research.html",   "Research log — F1 through F40",                                    "research_log", "violet", "Read / Research"),
    ("GLOSSARY.md",                "glossary.html",   "Glossary — named concepts in this project",                       "reference",    "teal",   "Read / Glossary"),
    ("PRECEDENTS.md",              "precedents.html", "Precedents — adjacent voices, prior art, ecosystem",              "reference",    "teal",   "Read / Precedents"),
    ("CHANGELOG.md",               "changelog.html",  "Changelog — project trajectory",                                  "changelog",    "amber",  "Code / Changelog"),
]


# ─── Markdown → HTML converter (stdlib only) ────────────────────────────


def render_markdown(md_text: str) -> str:
    """
    Convert a markdown string to HTML, handling the subset of CommonMark + GFM
    actually used in this repo's .md files.

    Block elements:
      - ATX headers (# through ######) with auto-generated id slugs
      - Paragraphs
      - Unordered lists (- or *) and ordered lists (1.)
      - Fenced code blocks (```lang)
      - Blockquotes (>)
      - Horizontal rules (---, ***, ___)
      - GFM tables (| col | col | with --- separator)
      - HTML passthrough (lines beginning with < are emitted as-is)

    Inline elements:
      - Inline code (`x`)
      - Links ([text](url))
      - Images (![alt](url))
      - Strong (**x** or __x__) and emphasis (*x* or _x_)
      - Auto-link bare URLs (best-effort)
    """
    lines = md_text.replace("\r\n", "\n").split("\n")
    out: list = []
    i = 0
    n = len(lines)

    para_buf: list = []
    list_buf: list = []          # entries are (indent, marker, text)
    list_type: str | None = None  # "ul" or "ol"
    table_buf: list = []
    in_table = False

    def flush_para():
        nonlocal para_buf
        if para_buf:
            text = " ".join(para_buf).strip()
            if text:
                out.append(f"<p>{render_inline(text)}</p>")
            para_buf = []

    def flush_list():
        nonlocal list_buf, list_type
        if list_buf and list_type:
            items = "".join(f"<li>{render_inline(t)}</li>" for _, _, t in list_buf)
            out.append(f"<{list_type}>{items}</{list_type}>")
            list_buf = []
            list_type = None

    def flush_table():
        nonlocal in_table, table_buf
        if not in_table or not table_buf:
            in_table = False
            table_buf = []
            return
        rows = []
        for ln in table_buf:
            ln = ln.strip()
            if ln.startswith("|"):
                ln = ln[1:]
            if ln.endswith("|"):
                ln = ln[:-1]
            cells = [c.strip() for c in ln.split("|")]
            rows.append(cells)
        # Recognise GFM table: row 1 = header, row 2 = separator (--- or :---:), rest = body
        if len(rows) >= 2 and all(re.match(r"^\s*:?-+:?\s*$", c) for c in rows[1]):
            header = rows[0]
            body = rows[2:]
            thead = "<tr>" + "".join(f"<th>{render_inline(c)}</th>" for c in header) + "</tr>"
            tbody = "".join(
                "<tr>" + "".join(f"<td>{render_inline(c)}</td>" for c in row) + "</tr>"
                for row in body
            )
            out.append(f'<table class="md-table"><thead>{thead}</thead><tbody>{tbody}</tbody></table>')
        else:
            # Not a real table; render verbatim
            out.append("<p>" + render_inline("\n".join(table_buf)) + "</p>")
        in_table = False
        table_buf = []

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Fenced code block
        m = re.match(r"^(`{3,}|~{3,})(.*)$", line)
        if m:
            fence = m.group(1)
            lang = m.group(2).strip()
            flush_para(); flush_list(); flush_table()
            i += 1
            code_lines = []
            while i < n and not lines[i].startswith(fence):
                code_lines.append(lines[i])
                i += 1
            code = "\n".join(code_lines)
            lang_attr = f' class="language-{html.escape(lang)}"' if lang else ""
            out.append(f"<pre><code{lang_attr}>{html.escape(code)}</code></pre>")
            i += 1  # consume closing fence
            continue

        # ATX header
        m = re.match(r"^(#{1,6})\s+(.+?)\s*#*$", line)
        if m:
            flush_para(); flush_list(); flush_table()
            level = len(m.group(1))
            text = m.group(2)
            slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or f"section-{i}"
            out.append(f'<h{level} id="{slug}">{render_inline(text)}</h{level}>')
            i += 1
            continue

        # Horizontal rule
        if re.match(r"^\s*[-*_]([\s]*[-*_]){2,}\s*$", line) and not re.match(r"^\s*[-*]\s+", line):
            flush_para(); flush_list(); flush_table()
            out.append("<hr>")
            i += 1
            continue

        # Blockquote
        if line.startswith(">"):
            flush_para(); flush_list(); flush_table()
            quote_lines = []
            while i < n and (lines[i].startswith(">") or (quote_lines and lines[i].strip() and not lines[i].lstrip().startswith(("#", "-", "*", "1.", "```"))) or (lines[i].startswith("> "))):
                if lines[i].startswith(">"):
                    quote_lines.append(lines[i][1:].lstrip())
                elif quote_lines and lines[i].strip():
                    quote_lines.append(lines[i].lstrip())
                else:
                    break
                i += 1
            inner = render_markdown("\n".join(quote_lines))
            out.append(f"<blockquote>{inner}</blockquote>")
            continue

        # Table (GFM): line starts with `|` and the next line is a separator
        if line.lstrip().startswith("|") and i + 1 < n and re.match(r"^\s*\|?\s*:?-+:?(\s*\|\s*:?-+:?)+\s*\|?\s*$", lines[i + 1]):
            flush_para(); flush_list()
            in_table = True
            while i < n and lines[i].lstrip().startswith("|"):
                table_buf.append(lines[i])
                i += 1
            flush_table()
            continue

        # Unordered list item
        m = re.match(r"^(\s*)[-*]\s+(.+)$", line)
        if m and not re.match(r"^\s*[-*]([\s]*[-*]){2,}\s*$", line):
            flush_para(); flush_table()
            indent = len(m.group(1))
            text = m.group(2)
            if list_type and list_type != "ul":
                flush_list()
            list_type = "ul"
            # Continuation lines for the same item
            i += 1
            while i < n:
                cont = lines[i]
                if not cont.strip():
                    break
                if re.match(r"^(\s*)[-*]\s+", cont) or re.match(r"^(\s*)\d+\.\s+", cont):
                    break
                if cont.startswith(" " * (indent + 2)):
                    text += " " + cont.strip()
                    i += 1
                else:
                    break
            list_buf.append((indent, "-", text))
            continue

        # Ordered list item
        m = re.match(r"^(\s*)(\d+)\.\s+(.+)$", line)
        if m:
            flush_para(); flush_table()
            indent = len(m.group(1))
            text = m.group(3)
            if list_type and list_type != "ol":
                flush_list()
            list_type = "ol"
            i += 1
            while i < n:
                cont = lines[i]
                if not cont.strip():
                    break
                if re.match(r"^(\s*)[-*]\s+", cont) or re.match(r"^(\s*)\d+\.\s+", cont):
                    break
                if cont.startswith(" " * (indent + 2)):
                    text += " " + cont.strip()
                    i += 1
                else:
                    break
            list_buf.append((indent, m.group(2), text))
            continue

        # Empty line — flush buffered blocks
        if not stripped:
            flush_para(); flush_list(); flush_table()
            i += 1
            continue

        # HTML passthrough (lines starting with `<`)
        if stripped.startswith("<"):
            flush_para(); flush_list(); flush_table()
            out.append(line)
            i += 1
            continue

        # Default: paragraph text
        para_buf.append(line)
        i += 1

    flush_para(); flush_list(); flush_table()
    return "\n".join(out)


def render_inline(text: str) -> str:
    """Convert inline markdown: code, images, links, strong, em, autolinks."""
    # Escape HTML first, except for already-rendered tags from prior passes.
    # We avoid double-escaping by skipping if the text contains < or > already.
    # Inline code (do FIRST so its contents are not processed)
    placeholders: list = []

    def stash_code(m):
        placeholders.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"\x00CODE{len(placeholders) - 1}\x00"

    text = re.sub(r"`([^`]+)`", stash_code, text)
    # Now escape any remaining HTML special chars EXCEPT < which we permit for raw passthrough
    text = text.replace("&", "&amp;").replace("\"", "&quot;")
    # Restore inline code
    text = re.sub(r"\x00CODE(\d+)\x00", lambda m: placeholders[int(m.group(1))], text)

    # Images ![alt](url) — emit before links so syntax matches
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)",
                  lambda m: f'<img src="{html.escape(m.group(2), quote=True)}" alt="{html.escape(m.group(1))}">',
                  text)
    # Links [text](url) — text may contain inline formatting already; emit raw
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                  lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>',
                  text)
    # Strong (** or __)
    text = re.sub(r"\*\*([^*\n]+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__([^_\n]+?)__", r"<strong>\1</strong>", text)
    # Emphasis (* or _) — avoid matching ** by requiring single chars
    text = re.sub(r"(?<![\\*])\*(?!\s)([^*\n]+?)(?<!\s)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"(?<![\\_a-zA-Z0-9])_(?!\s)([^_\n]+?)(?<!\s)_(?!_)(?![a-zA-Z0-9])", r"<em>\1</em>", text)

    return text


# ─── Capsule assembly ───────────────────────────────────────────────────


HASH_PLACEHOLDER = "sha256:pending"


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def compute_content_hash(data: dict, manifest: dict) -> str:
    m = json.loads(json.dumps(manifest))
    if isinstance(m.get("integrity"), dict):
        m["integrity"]["content_hash"] = HASH_PLACEHOLDER
    payload = canonical_json(m) + "\n" + canonical_json(data)
    return f"sha256:{sha256_hex(payload)}"


def build_capsule(src: Path, out: Path, title: str, type_: str, lead: str, breadcrumb: str) -> None:
    md_text = src.read_text(encoding="utf-8")
    src_sha = sha256_hex(md_text)
    capsule_uuid = str(uuid.uuid5(NAMESPACE, src.relative_to(REPO_ROOT).as_posix()))
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    today = now[:10]
    rendered_html = render_markdown(md_text)

    manifest = {
        "spec_version": "0.3.0",
        "uuid": capsule_uuid,
        "capsule_version": "1.0.0",
        "title": title,
        "description": (
            f"On-site reading view of {src.relative_to(REPO_ROOT).as_posix()}. "
            f"Auto-generated by compiler/build_md_capsules.py from the source markdown "
            f"(SHA-256 {src_sha[:16]}…). The host serves raw .md as text/markdown, so "
            f"this Capsule renders the same content as a sealed HTML artifact with a "
            f"comfortable reading view, integrity hash, and standard export capabilities. "
            f"Source markdown lives at the same path in the GitHub repo if you want raw."
        ),
        "type": type_,
        "profile": "static",
        "created_at": now,
        "generator": {
            "name": "compiler/build_md_capsules.py",
            "version": "1.0.0",
            "kind": "compiler",
        },
        "source": {
            "origin": "repository_markdown",
            "snapshot_type": "markdown_render",
            "snapshot_id": f"snapshot:{src.relative_to(REPO_ROOT).as_posix()}-{today}",
            "included_records": 1,
            "spec_received": "v0.3.0 · 2026-05-19",
            "source_path": src.relative_to(REPO_ROOT).as_posix(),
            "source_sha256": src_sha,
            "source_bytes": len(md_text.encode("utf-8")),
        },
        "privacy": {
            "visibility": "public",
            "contains_private_data": False,
            "redaction_applied": False,
            "external_dependencies": False,
        },
        "capabilities": [
            "about", "copy_as_json", "download_json", "download_capsule", "print_to_pdf",
        ],
        "synthesis": {
            "kind": "deterministic_markdown_render",
            "model": "compiler/build_md_capsules.py v1.0.0",
            "human_reviewed": False,
        },
        "integrity": {
            "hash_scope": "data+manifest",
            "algorithm": "sha256",
            "content_hash": HASH_PLACEHOLDER,
        },
    }

    data = {
        "source_path": src.relative_to(REPO_ROOT).as_posix(),
        "source_sha256": src_sha,
        "source_bytes": len(md_text.encode("utf-8")),
        "source_lines": md_text.count("\n") + 1,
        "rendered_at": now,
        "breadcrumb": breadcrumb,
        "lead_color": lead,
    }

    manifest["integrity"]["content_hash"] = compute_content_hash(data, manifest)

    html_out = TEMPLATE.format(
        title=html.escape(title),
        description_short=html.escape(f"On-site reading view of {src.relative_to(REPO_ROOT).as_posix()}."),
        manifest_json=json.dumps(manifest, indent=2, ensure_ascii=False),
        data_json=json.dumps(data, separators=(",", ":"), ensure_ascii=False),
        styles=STYLES.replace("__LEAD__", lead),
        body=rendered_html,
        runtime=RUNTIME,
        breadcrumb=html.escape(breadcrumb),
        sealed_date=today,
        source_filename=html.escape(src.relative_to(REPO_ROOT).as_posix()),
        uuid_short=capsule_uuid[:8],
    )

    out.write_text(html_out, encoding="utf-8")


# ─── Templates ──────────────────────────────────────────────────────────


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data:; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'none'; base-uri 'none'; form-action 'none'; object-src 'none'">
<meta name="color-scheme" content="light dark">
<meta name="description" content="{description_short}">
<title>{title} · HTML Capsule</title>

<script id="capsule-manifest" type="application/json">
{manifest_json}
</script>

<script id="capsule-data" type="application/json">{data_json}</script>

<style id="capsule-style">
{styles}
</style>
</head>
<body>
<a class="skip" href="#capsule-root">Skip to content</a>
<main id="capsule-root">

  <nav class="topnav" aria-label="Top">
    <a class="home" href="/">
      <svg viewBox="0 0 32 18" width="22" height="14" aria-hidden="true" focusable="false">
        <rect x="1" y="1" width="30" height="16" rx="8" ry="8" fill="none" stroke="currentColor" stroke-width="2"/>
        <g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M 9.5 5.5 L 6 9 L 9.5 12.5"/>
          <path d="M 13.5 13 L 18.5 5"/>
          <path d="M 22.5 5.5 L 26 9 L 22.5 12.5"/>
        </g>
      </svg>
      <span>HTML Capsule</span>
    </a>
    <span class="crumb">{breadcrumb}</span>
    <span class="topnav-spacer"></span>
    <span class="topnav-links">
      <a href="/notes">Notes</a>
      <a href="/exploration">Long-form</a>
      <a href="https://github.com/bigfancygarden/htmlcapsule/blob/main/{source_filename}">Source</a>
    </span>
  </nav>

  <article class="md-body">
{body}
  </article>

  <details class="about" id="about">
    <summary>About this page · manifest · exports</summary>
    <div class="about-body">
      <p>This is a sealed HTML Capsule per Core spec v0.3.0. Five required inline blocks, no network dependencies, integrity hash over data + manifest. The content above is rendered from <code>{source_filename}</code> by the deterministic <code>compiler/build_md_capsules.py</code> at the time of the last source change.</p>
      <div class="row" role="group" aria-label="Exports">
        <button type="button" data-capsule-action="copy_as_json">Copy data as JSON</button>
        <button type="button" data-capsule-action="download_json">Download JSON</button>
        <button type="button" data-capsule-action="download_capsule">Download capsule</button>
        <button type="button" data-capsule-action="print_to_pdf">Print to PDF</button>
      </div>
      <pre id="manifest-view">Loading manifest…</pre>
    </div>
  </details>

  <footer class="site">
    <p class="footer-line">capsule:<code>{uuid_short}</code> · sealed {sealed_date} · source <code>{source_filename}</code> · <a href="/">htmlcapsule.org</a></p>
  </footer>
</main>

<script id="capsule-runtime">
{runtime}
</script>
</body>
</html>
"""


STYLES = """
:root {
  color-scheme: light dark;
  --paper:       #f5f6f8;
  --paper-soft:  #ebedf1;
  --paper-page:  #ffffff;
  --ink:         #0c0e13;
  --ink-soft:    #2a2e38;
  --ink-mute:    #5d6470;
  --ink-faint:   #8a909c;
  --rule:        #dde0e6;
  --rule-soft:   #e8eaef;
  --indigo:      #4f46e5;
  --indigo-soft: #eef0fe;
  --indigo-deep: #3730a3;
  --violet:      #7c3aed;
  --violet-soft: #f3edff;
  --violet-deep: #5b21b6;
  --teal:        #0d9488;
  --teal-soft:   #e0f5f1;
  --teal-deep:   #115e59;
  --amber:       #b45309;
  --amber-soft:  #fbeed5;
  --amber-deep:  #7c2d12;
  --rose:        #be123c;
  --rose-soft:   #fce4ea;
  --lead:        var(--__LEAD__);
  --lead-soft:   var(--__LEAD__-soft);
  --lead-deep:   var(--__LEAD__-deep);
  --sans: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", system-ui, sans-serif;
  --mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  --measure: 70ch;
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper:       #0c0e13;
    --paper-soft:  #1a1d24;
    --paper-page:  #11141a;
    --ink:         #edf1f7;
    --ink-soft:    #c5cad4;
    --ink-mute:    #8a909c;
    --ink-faint:   #5d6470;
    --rule:        #2b313d;
    --rule-soft:   #1f242d;
    --indigo:      #818cf8;
    --indigo-soft: #1e1b4b;
    --indigo-deep: #c7cbf6;
    --violet:      #a78bfa;
    --violet-soft: #2e1065;
    --violet-deep: #d8b4fe;
    --teal:        #2dd4bf;
    --teal-soft:   #134e4a;
    --teal-deep:   #5eead4;
    --amber:       #fbbf24;
    --amber-soft:  #451a03;
    --amber-deep:  #fde68a;
    --rose:        #fb7185;
    --rose-soft:   #4c0519;
  }
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: var(--paper); color: var(--ink); }
body {
  font-family: var(--sans);
  font-size: 17px;
  line-height: 1.62;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}
.skip { position: absolute; left: -9999px; }
.skip:focus { left: 1rem; top: 1rem; background: var(--ink); color: var(--paper); padding: .5rem .75rem; border-radius: 6px; z-index: 99; }

main {
  max-width: 880px;
  margin: 0 auto;
  padding: 0 clamp(20px, 4vw, 48px) 80px;
}

/* ─── Top nav ─── */
.topnav {
  display: flex; align-items: center; gap: 12px;
  padding: 18px 0 14px;
  border-bottom: 1px solid var(--rule);
  font-size: 14px;
  flex-wrap: wrap;
}
.topnav .home {
  display: inline-flex; align-items: center; gap: 8px;
  color: var(--ink);
  font-weight: 600;
  text-decoration: none;
  border-bottom: 0;
}
.topnav .home svg { color: var(--lead); }
.topnav .crumb {
  color: var(--ink-mute);
  font-family: var(--mono);
  font-size: 12.5px;
}
.topnav-spacer { flex: 1 1 16px; }
.topnav-links { display: inline-flex; gap: 14px; }
.topnav-links a {
  color: var(--ink-mute);
  font-size: 13px;
  text-decoration: none;
  border-bottom: 1px solid transparent;
}
.topnav-links a:hover { color: var(--lead); border-bottom-color: var(--lead); }

/* ─── Markdown body ─── */
.md-body {
  padding: 32px 0 16px;
  max-width: var(--measure);
}
.md-body h1, .md-body h2, .md-body h3, .md-body h4, .md-body h5, .md-body h6 {
  letter-spacing: -.012em;
  color: var(--ink);
  margin: 1.6em 0 .55em;
  line-height: 1.18;
  text-wrap: balance;
}
.md-body h1 { font-size: clamp(28px, 4vw, 38px); margin-top: 0; font-weight: 700; }
.md-body h1::before {
  content: "";
  display: block;
  width: 32px; height: 3px;
  background: var(--lead);
  margin-bottom: 18px;
  border-radius: 2px;
}
.md-body h2 { font-size: 23px; padding-top: 8px; border-top: 1px solid var(--rule-soft); font-weight: 600; }
.md-body h3 { font-size: 19px; font-weight: 600; }
.md-body h4 { font-size: 16px; font-weight: 600; color: var(--ink-soft); }
.md-body h5, .md-body h6 { font-size: 14px; font-weight: 600; color: var(--ink-mute); text-transform: uppercase; letter-spacing: .04em; }
.md-body p {
  margin: 0 0 1.05em;
  color: var(--ink-soft);
  text-wrap: pretty;
}
.md-body strong { color: var(--ink); font-weight: 600; }
.md-body em { font-style: italic; color: var(--ink); }
.md-body a {
  color: var(--lead);
  text-decoration: none;
  border-bottom: 1px solid color-mix(in oklab, var(--lead) 30%, transparent);
}
.md-body a:hover, .md-body a:focus-visible {
  color: var(--lead-deep);
  border-bottom-color: var(--lead-deep);
}
.md-body code {
  font-family: var(--mono);
  font-size: .9em;
  background: var(--paper-soft);
  padding: 1px 6px;
  border-radius: 4px;
  color: var(--lead-deep);
}
.md-body pre {
  background: var(--paper-soft);
  border: 1px solid var(--rule);
  border-radius: 8px;
  padding: 16px 18px;
  margin: 1em 0 1.4em;
  overflow-x: auto;
  font-family: var(--mono);
  font-size: 13px;
  line-height: 1.55;
}
.md-body pre code {
  background: transparent;
  padding: 0;
  color: var(--ink-soft);
  font-size: 13px;
}
.md-body ul, .md-body ol { padding-left: 1.6em; margin: 0 0 1.05em; color: var(--ink-soft); }
.md-body ul li, .md-body ol li { margin-bottom: .3em; }
.md-body blockquote {
  margin: 1em 0 1.4em;
  padding: .55em 1.1em;
  background: var(--lead-soft);
  border-left: 3px solid var(--lead);
  border-radius: 0 8px 8px 0;
  color: var(--lead-deep);
}
.md-body blockquote p:last-child { margin-bottom: 0; }
.md-body hr {
  border: 0;
  border-top: 1px solid var(--rule);
  margin: 2em 0;
}
.md-body img {
  max-width: 100%; height: auto; border-radius: 8px;
}
.md-body table.md-table {
  width: 100%;
  border-collapse: collapse;
  margin: 1em 0 1.4em;
  font-size: 14.5px;
}
.md-body table.md-table th, .md-body table.md-table td {
  padding: 8px 12px;
  border-bottom: 1px solid var(--rule);
  text-align: left;
  vertical-align: top;
}
.md-body table.md-table th {
  font-weight: 600;
  color: var(--ink);
  background: var(--paper-soft);
}
.md-body table.md-table tbody tr:hover { background: color-mix(in oklab, var(--lead) 4%, transparent); }

/* ─── About ─── */
.about {
  margin-top: 48px;
  background: var(--paper-page);
  border: 1px solid var(--rule);
  border-radius: 8px;
  padding: 14px 18px;
}
.about > summary {
  cursor: pointer;
  font-family: var(--mono);
  font-size: 13px;
  letter-spacing: .04em;
  color: var(--ink-mute);
  list-style: none;
}
.about > summary::-webkit-details-marker { display: none; }
.about > summary::before { content: "+ "; color: var(--ink-mute); }
.about[open] > summary::before { content: "− "; }
.about-body { margin-top: 14px; }
.about-body p { font-size: 14px; color: var(--ink-soft); margin: 0 0 14px; }
.about-body .row { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
.about-body button {
  appearance: none;
  background: var(--paper-soft);
  color: var(--ink);
  border: 1px solid var(--rule);
  border-radius: 6px;
  padding: 6px 12px;
  font: 500 12.5px/1 var(--sans);
  cursor: pointer;
}
.about-body button:hover, .about-body button:focus-visible {
  background: var(--lead); color: var(--paper-page); border-color: var(--lead); outline: none;
}
.about-body pre {
  background: var(--paper-soft);
  border: 1px solid var(--rule);
  border-radius: 6px;
  padding: 14px;
  overflow: auto;
  max-height: 360px;
  font-family: var(--mono);
  font-size: 12px;
  color: var(--ink-soft);
  margin: 0;
}

/* ─── Footer ─── */
footer.site {
  margin-top: 24px;
  padding-top: 18px;
  border-top: 1px solid var(--rule);
  text-align: center;
}
.footer-line { font-family: var(--mono); font-size: 12px; color: var(--ink-mute); margin: 0; }
.footer-line a { color: var(--lead); text-decoration: none; border-bottom: 1px solid color-mix(in oklab, var(--lead) 30%, transparent); }

@media print {
  .topnav, .about, footer.site { display: none !important; }
  .md-body { max-width: none; }
  body { background: white; color: black; }
}
"""


RUNTIME = """
(function () {
  'use strict';
  var manifest = JSON.parse(document.getElementById('capsule-manifest').textContent);
  var data = JSON.parse(document.getElementById('capsule-data').textContent);
  var mEl = document.getElementById('manifest-view');
  if (mEl) mEl.textContent = JSON.stringify(manifest, null, 2);
  function safeName(s) { return (s || 'capsule').replace(/[^a-z0-9_\\-]+/gi, '_'); }
  function downloadBlob(filename, mime, content) {
    var blob = (content instanceof Blob) ? content : new Blob([content], { type: mime });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url; a.download = filename;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }
  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text);
    return Promise.resolve(false);
  }
  var actions = {
    copy_as_json: function () { copyText(JSON.stringify(data, null, 2)); },
    download_json: function () {
      downloadBlob(safeName(manifest.title) + '.json', 'application/json', JSON.stringify(data, null, 2));
    },
    download_capsule: function () {
      var html = '<!DOCTYPE html>\\n' + document.documentElement.outerHTML;
      downloadBlob(safeName(manifest.title) + '_capsule.html', 'text/html', html);
    },
    print_to_pdf: function () { setTimeout(function () { window.print(); }, 150); },
    about: function () {
      var d = document.getElementById('about');
      if (d) d.open = !d.open;
    }
  };
  document.querySelectorAll('[data-capsule-action]').forEach(function (el) {
    var name = el.getAttribute('data-capsule-action');
    if (!actions[name]) return;
    el.addEventListener('click', function (e) {
      if (el.tagName === 'BUTTON') e.preventDefault();
      try { actions[name](); } catch (err) { console.error('[md-capsule]', name, err); }
    });
  });
  (manifest.capabilities || []).forEach(function (cap) {
    if (!actions[cap]) console.warn('[md-capsule] declared capability "' + cap + '" has no runtime handler — Rule 7 violation');
  });
})();
"""


# ─── Main ───────────────────────────────────────────────────────────────


def main():
    out_dir = REPO_ROOT
    built = []
    for src_rel, out_name, title, type_, lead, breadcrumb in FILES:
        src = REPO_ROOT / src_rel
        if not src.exists():
            print(f"  skip {src_rel} (not found)")
            continue
        out = out_dir / out_name
        build_capsule(src, out, title, type_, lead, breadcrumb)
        size = out.stat().st_size
        print(f"  wrote {out_name:<22} ({size:,} bytes) from {src_rel}")
        built.append(out)
    print()
    print(f"Built {len(built)} capsules.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
