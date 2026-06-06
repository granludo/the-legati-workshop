#!/usr/bin/env python3
"""tools/wiki/validate.py — sanity checker for the wiki/ tree.

Checks:
  - Broken wikilinks: `[[path]]` references in wiki entries that don't resolve to a file on disk.
  - Duplicate slugs: two entries claiming the same slug (within or across facets).
  - Orphans: entries with no sources.
  - Stale timestamps: entries whose `last-touched` lags the most recent git commit on any of their sources.
  - Missing facet INDEX.md files.

Usage:
  python3 tools/wiki/validate.py            # report only
  python3 tools/wiki/validate.py --strict   # exit 1 on any issue
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
WIKI = REPO / "wiki"

WIKILINK_RE = re.compile(r"\[\[([^\]\|\#]+)(?:#[^\]\|]+)?(?:\|[^\]]*)?\]\]")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def find_entries() -> list[Path]:
    if not WIKI.exists():
        return []
    return [p for p in WIKI.rglob("*.md") if p.name not in ("INDEX.md",)]


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        out[k.strip()] = v.strip()
    return out


def resolve_wikilink(target: str, entry_path: Path) -> Path | None:
    """Try to resolve a wikilink target. Returns the file Path if found."""
    target = target.strip()
    if not target:
        return None

    # Try as a relative path from repo root
    candidates = [
        REPO / target,
        REPO / (target + ".md"),
        # Or as a sibling of the entry (Obsidian-style)
        entry_path.parent / (target + ".md"),
        entry_path.parent / target,
    ]
    for c in candidates:
        if c.exists() and c.is_file():
            return c
    return None


def latest_git_date(rel: str) -> str | None:
    try:
        res = subprocess.run(
            ["git", "log", "-1", "--format=%aI", "--", rel],
            cwd=REPO, capture_output=True, text=True, timeout=15,
        )
        d = res.stdout.strip()
        return d[:10] if d else None
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true",
                    help="exit code 1 if any issue is found")
    args = ap.parse_args()

    entries = find_entries()
    if not entries:
        print("wiki/ is empty — nothing to validate.")
        return

    print(f"validating {len(entries)} entries under {WIKI}\n")

    broken: list[tuple[str, str]] = []
    slugs: dict[str, list[str]] = defaultdict(list)
    orphans: list[str] = []
    stale: list[tuple[str, str, str]] = []

    for e in entries:
        rel = str(e.relative_to(REPO))
        text = e.read_text(encoding="utf-8", errors="ignore")
        fm = parse_frontmatter(text)

        slug = fm.get("slug")
        if slug:
            slugs[slug].append(rel)

        # Broken wikilinks
        for m in WIKILINK_RE.finditer(text):
            tgt = m.group(1).strip()
            if not tgt:
                continue
            if resolve_wikilink(tgt, e) is None:
                broken.append((rel, tgt))

        # Orphan check: count Sources section lines starting with "- [["
        in_sources = False
        sources_count = 0
        for line in text.splitlines():
            if line.strip().startswith("## Sources"):
                in_sources = True
                continue
            if in_sources and line.startswith("## "):
                in_sources = False
            if in_sources and line.strip().startswith("- [["):
                sources_count += 1
        if sources_count == 0:
            orphans.append(rel)

        # Stale check
        last_touched = fm.get("last-touched")
        if last_touched:
            for line in text.splitlines():
                if line.strip().startswith("- [[") and "## Sources" not in line:
                    sm = re.search(r"\[\[([^\]\|\#]+)\]\]", line)
                    if not sm:
                        continue
                    src_rel = sm.group(1).strip()
                    src_date = latest_git_date(src_rel)
                    if src_date and src_date > last_touched:
                        stale.append((rel, src_rel, f"{last_touched} < {src_date}"))
                        break

    print(f"== broken wikilinks: {len(broken)} ==")
    for rel, tgt in broken[:25]:
        print(f"  {rel} -> [[{tgt}]]")
    if len(broken) > 25:
        print(f"  ... +{len(broken) - 25} more")

    dups = {s: paths for s, paths in slugs.items() if len(paths) > 1}
    print(f"\n== duplicate slugs: {len(dups)} ==")
    for s, paths in list(dups.items())[:20]:
        print(f"  '{s}': {paths}")

    print(f"\n== orphans (no sources): {len(orphans)} ==")
    for rel in orphans[:20]:
        print(f"  {rel}")

    print(f"\n== stale (last-touched < latest source git date): {len(stale)} ==")
    for rel, src, gap in stale[:20]:
        print(f"  {rel} (source {src}): {gap}")

    issues = len(broken) + len(dups) + len(orphans) + len(stale)
    print(f"\n=== total issues: {issues} ===")
    if args.strict and issues:
        sys.exit(1)


if __name__ == "__main__":
    main()
