"""Safe markdown → HTML for chat bubbles (escape-first, limited transforms)."""

from __future__ import annotations

import html
import re


_FENCE_RE = re.compile(r"```([a-zA-Z0-9_+-]*)\n(.*?)```", re.DOTALL)


def markdown_to_safe_html(text: str) -> str:
    """
    Convert a limited markdown subset to HTML after HTML-escaping.
    Supports: paragraphs, **bold**, *italic*, `code`, fenced code blocks,
    unordered/ordered lists, simple GFM tables, and soft line breaks.
    """
    if not text:
        return ""

    fences: list[str] = []

    def _store_fence(match: re.Match) -> str:
        lang = match.group(1) or ""
        code = match.group(2)
        safe_code = html.escape(code.rstrip("\n"))
        lang_attr = f' data-lang="{html.escape(lang)}"' if lang else ""
        fences.append(f"<pre{lang_attr}><code>{safe_code}</code></pre>")
        return f"\n@@FENCE{len(fences) - 1}@@\n"

    working = _FENCE_RE.sub(_store_fence, text)
    escaped = html.escape(working)

    # Inline code
    escaped = re.sub(r"`([^`\n]+)`", r"<code>\1</code>", escaped)

    # Bold then italic
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", escaped)

    blocks = re.split(r"\n\s*\n", escaped.strip())
    html_parts: list[str] = []

    for block in blocks:
        block = block.strip()
        if not block:
            continue
        if re.fullmatch(r"@@FENCE\d+@@", block):
            html_parts.append(block)
            continue

        table_html = _try_table(block)
        if table_html:
            html_parts.append(table_html)
            continue

        lines = block.split("\n")
        if all(re.match(r"^[-*]\s+", ln) for ln in lines):
            items = [re.sub(r"^[-*]\s+", "", ln) for ln in lines]
            html_parts.append("<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>")
        elif all(re.match(r"^\d+\.\s+", ln) for ln in lines):
            items = [re.sub(r"^\d+\.\s+", "", ln) for ln in lines]
            html_parts.append("<ol>" + "".join(f"<li>{i}</li>" for i in items) + "</ol>")
        else:
            html_parts.append("<p>" + "<br>".join(lines) + "</p>")

    out = "\n".join(html_parts)
    for i, fence_html in enumerate(fences):
        out = out.replace(f"@@FENCE{i}@@", fence_html)
    return out


def _try_table(block: str) -> str | None:
    """Parse a simple pipe table; return None if not a table."""
    lines = [ln.strip() for ln in block.split("\n") if ln.strip()]
    if len(lines) < 2 or not all("|" in ln for ln in lines):
        return None

    sep_cells = [c.strip() for c in lines[1].strip().strip("|").split("|")]
    if not sep_cells or not all(re.fullmatch(r":?-{3,}:?", c.replace(" ", "")) for c in sep_cells):
        return None

    def split_row(row: str) -> list[str]:
        return [c.strip() for c in row.strip().strip("|").split("|")]

    header = split_row(lines[0])
    if not header:
        return None

    thead = "<thead><tr>" + "".join(f"<th>{c}</th>" for c in header) + "</tr></thead>"
    body_rows = []
    for ln in lines[2:]:
        row = split_row(ln)
        padded = (row + [""] * len(header))[: len(header)]
        body_rows.append("<tr>" + "".join(f"<td>{c}</td>" for c in padded) + "</tr>")
    tbody = "<tbody>" + "".join(body_rows) + "</tbody>"
    return f'<div class="sakoon-table-wrap"><table class="sakoon-md-table">{thead}{tbody}</table></div>'
