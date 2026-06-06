#!/usr/bin/env python3
"""tools/wiki/render_indexes.py — generate INDEX.md (alphabetical + by-relevance)
+ JSON sidecar + self-contained sortable HTML for each facet.

Outputs per facet (persons / topics / key-ideas / projects):
  wiki/<facet>/INDEX.md     — alphabetical table + by-relevance section
  wiki/<facet>/_data.json   — single-source-of-truth metadata
  wiki/<facet>/index.html   — self-contained sortable/filterable view

Usage:
  python3 tools/wiki/render_indexes.py
  python3 tools/wiki/render_indexes.py --facet persons    # one facet only
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
WIKI = REPO / "wiki"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
FACETS = ["persons", "topics", "key-ideas", "projects"]


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm = {}
    in_list_key = None
    for line in m.group(1).splitlines():
        if line.startswith("  - ") and in_list_key:
            fm.setdefault(in_list_key, []).append(line[4:].strip())
            continue
        in_list_key = None
        if ":" in line:
            k, v = line.split(":", 1)
            v = v.strip()
            if v == "":
                in_list_key = k.strip()
                fm[in_list_key] = []
            else:
                fm[k.strip()] = v
    return fm


def parse_sources_count(text: str) -> int:
    in_section = False
    n = 0
    for line in text.splitlines():
        if line.strip() == "## Sources":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.strip().startswith("- [["):
            n += 1
    return n


def collect_entries(facet: str) -> list[dict]:
    facet_dir = WIKI / facet
    if not facet_dir.exists():
        return []
    out = []
    for p in sorted(facet_dir.glob("*.md")):
        if p.name == "INDEX.md":
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        fm = parse_frontmatter(text)
        sources = parse_sources_count(text)
        try:
            sources_fm = int(fm.get("sources-count", "0"))
        except Exception:
            sources_fm = 0
        out.append({
            "slug": p.stem,
            "name": fm.get("name", p.stem).strip('"').strip("'"),
            "sources": max(sources, sources_fm),
            "first_seen": fm.get("first-seen", ""),
            "last_touched": fm.get("last-touched", ""),
            "aliases": fm.get("aliases", []) or [],
            "roles": fm.get("roles", []) or [],
            "status": fm.get("status", "active"),
        })
    return out


def render_md(facet: str, entries: list[dict]) -> str:
    now = datetime.now().isoformat(timespec="seconds")
    by_name = sorted(entries, key=lambda e: e["name"].casefold())
    by_relevance = sorted(entries, key=lambda e: (-e["sources"], e["name"].casefold()))

    lines = [
        f"# wiki/{facet}/ — INDEX",
        "",
        f"Auto-generated {now}. **{len(entries)}** entries.",
        "",
        f"For an interactive sortable / filterable view, open [`index.html`](index.html) in a browser. The browser table reads from `_data.json`.",
        "",
    ]

    # Role facets (currently only meaningful for persons)
    if facet == "persons":
        ROLE_ORDER = ["inner-circle", "contact", "co-author"]
        ROLE_LABELS = {
            "inner-circle": "Inner circle",
            "contact": "Contacts",
            "co-author": "Co-authors",
        }
        lines.append("## By role")
        lines.append("")
        for role in ROLE_ORDER:
            members = sorted(
                (e for e in entries if role in e["roles"]),
                key=lambda e: e["name"].casefold(),
            )
            if not members:
                continue
            lines.append(f"### {ROLE_LABELS[role]} ({len(members)})")
            lines.append("")
            for e in members:
                other_roles = [r for r in e["roles"] if r != role]
                tag = f" *({', '.join(other_roles)})*" if other_roles else ""
                lines.append(f"- [[{facet}/{e['slug']}\\|{e['name']}]]{tag}")
            lines.append("")
        cited_count = sum(1 for e in entries if not e["roles"])
        lines.append(f"### Cited only ({cited_count})")
        lines.append("")
        lines.append(f"*{cited_count} entries with no role tag — external references, historical figures, mentioned-once names. See the full alphabetical table below.*")
        lines.append("")

    lines.extend([
        "## By relevance (top by source count)",
        "",
        "| Slug | Name | Sources | Aliases |",
        "| --- | --- | --- | --- |",
    ])
    for e in by_relevance[:50]:
        aliases = ", ".join(e["aliases"][:3]) if e["aliases"] else ""
        lines.append(f"| [[{facet}/{e['slug']}\\|{e['slug']}]] | {e['name']} | {e['sources']} | {aliases} |")
    if len(by_relevance) > 50:
        lines.append("")
        lines.append(f"*+{len(by_relevance) - 50} more — see `index.html` for the full table.*")
    lines.append("")
    lines.append("## Alphabetical (full)")
    lines.append("")
    lines.append("| Slug | Name | Sources |")
    lines.append("| --- | --- | --- |")
    for e in by_name:
        lines.append(f"| [[{facet}/{e['slug']}\\|{e['slug']}]] | {e['name']} | {e['sources']} |")
    return "\n".join(lines) + "\n"


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>wiki/{facet}/ — sortable index</title>
<style>
:root {{ color-scheme: light dark; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif; margin: 1.5rem; max-width: 1200px; }}
h1 {{ margin: 0 0 0.5rem 0; }}
.meta {{ color: #888; font-size: 0.9em; margin-bottom: 1rem; }}
.controls {{ margin-bottom: 1rem; display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; }}
.controls input[type=text] {{ padding: 0.4rem 0.6rem; font-size: 1em; min-width: 320px; }}
.controls button {{ padding: 0.3rem 0.7rem; font-size: 0.9em; cursor: pointer; }}
.count {{ color: #888; font-size: 0.9em; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ text-align: left; padding: 0.4rem 0.6rem; border-bottom: 1px solid #888; }}
th {{ cursor: pointer; user-select: none; position: sticky; top: 0; background: var(--bg, #fff); }}
@media (prefers-color-scheme: dark) {{ th {{ background: #1a1a1a; }} }}
th.asc::after {{ content: " ▲"; opacity: 0.7; }}
th.desc::after {{ content: " ▼"; opacity: 0.7; }}
tr:hover {{ background: rgba(127,127,127,0.1); }}
.aliases {{ color: #888; font-size: 0.9em; }}
a {{ color: inherit; text-decoration: underline; text-decoration-thickness: 1px; }}
</style>
</head>
<body>
<h1>wiki/{facet}/</h1>
<div class="meta">Generated <span id="ts">{ts}</span> · <span id="total">{count}</span> entries.</div>
<div class="controls">
  <input type="text" id="filter" placeholder="filter by name, slug, alias…" autofocus>
  <button id="reset">reset</button>
  <span class="count" id="visible-count"></span>
</div>
<table id="t">
<thead>
<tr>
  <th data-key="name" data-type="str">Name</th>
  <th data-key="slug" data-type="str">Slug</th>
  <th data-key="sources" data-type="num" class="desc">Sources</th>
  <th data-key="aliases" data-type="str">Aliases</th>
  <th data-key="last_touched" data-type="str">Last touched</th>
</tr>
</thead>
<tbody id="tbody"></tbody>
</table>
<script id="data" type="application/json">{data_json}</script>
<script>
(function() {{
  const data = JSON.parse(document.getElementById("data").textContent);
  const tbody = document.getElementById("tbody");
  const filterEl = document.getElementById("filter");
  const resetEl = document.getElementById("reset");
  const visibleCount = document.getElementById("visible-count");
  let sortKey = "sources", sortDir = -1;

  function render() {{
    const q = filterEl.value.trim().toLowerCase();
    let rows = data.filter(d => {{
      if (!q) return true;
      const hay = [d.name, d.slug, ...(d.aliases || [])].join(" ").toLowerCase();
      return hay.includes(q);
    }});
    rows.sort((a, b) => {{
      const va = (a[sortKey] === undefined || a[sortKey] === null) ? "" : a[sortKey];
      const vb = (b[sortKey] === undefined || b[sortKey] === null) ? "" : b[sortKey];
      if (typeof va === "number" && typeof vb === "number") return (va - vb) * sortDir;
      return (String(va).localeCompare(String(vb))) * sortDir;
    }});
    tbody.innerHTML = rows.map(d => `
      <tr>
        <td>${{escapeHtml(d.name)}}</td>
        <td><a href="${{encodeURIComponent(d.slug)}}.md">${{escapeHtml(d.slug)}}</a></td>
        <td>${{d.sources}}</td>
        <td class="aliases">${{(d.aliases || []).map(escapeHtml).join(", ")}}</td>
        <td>${{escapeHtml(d.last_touched || "")}}</td>
      </tr>
    `).join("");
    visibleCount.textContent = `(${{rows.length}} shown)`;
    document.querySelectorAll("th").forEach(th => {{
      th.classList.remove("asc", "desc");
      if (th.dataset.key === sortKey) {{
        th.classList.add(sortDir === 1 ? "asc" : "desc");
      }}
    }});
  }}

  function escapeHtml(s) {{
    return String(s || "").replace(/[&<>"']/g, c => ({{"&":"&amp;","<":"&lt;",">":"&gt;","\\"":"&quot;","'":"&#39;"}}[c]));
  }}

  document.querySelectorAll("th").forEach(th => {{
    th.addEventListener("click", () => {{
      const k = th.dataset.key;
      if (k === sortKey) sortDir = -sortDir;
      else {{ sortKey = k; sortDir = (th.dataset.type === "num") ? -1 : 1; }}
      render();
    }});
  }});
  filterEl.addEventListener("input", render);
  resetEl.addEventListener("click", () => {{ filterEl.value = ""; sortKey = "sources"; sortDir = -1; render(); }});
  render();
}})();
</script>
</body>
</html>
"""


def render_html(facet: str, entries: list[dict]) -> str:
    payload = json.dumps(entries, ensure_ascii=False).replace("</", "<\\/")
    return HTML_TEMPLATE.format(
        facet=facet,
        ts=datetime.now().isoformat(timespec="seconds"),
        count=len(entries),
        data_json=payload,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--facet", choices=FACETS, default=None)
    args = ap.parse_args()

    facets = [args.facet] if args.facet else FACETS
    for facet in facets:
        entries = collect_entries(facet)
        if not entries:
            print(f"  {facet}: 0 entries (skipped)")
            continue
        (WIKI / facet / "INDEX.md").write_text(render_md(facet, entries), encoding="utf-8")
        (WIKI / facet / "_data.json").write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
        (WIKI / facet / "index.html").write_text(render_html(facet, entries), encoding="utf-8")
        print(f"  {facet}: {len(entries)} entries → INDEX.md + _data.json + index.html")


if __name__ == "__main__":
    main()
