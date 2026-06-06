#!/usr/bin/env python3
"""tools/wiki/apply_merges.py — apply approved merges from _approved-merges-<facet>.yaml.

For each merge with `approved: true`:
  1. Pick the canonical entry (creating it if its slug isn't yet a file).
  2. Union the merged-away entries' sources, contexts, frontmatter into the canonical.
  3. Add the merged-away names to canonical's `aliases:` frontmatter.
  4. Move merged-away entries to archive/wiki-merges/<date>/<facet>/<slug>.md
     (NOT deleted — reversible).
  5. Re-link any wiki entries that wikilinked to a merged-away slug → canonical.

Usage:
  python3 tools/wiki/apply_merges.py persons --dry-run     # show what would happen
  python3 tools/wiki/apply_merges.py persons               # apply
  python3 tools/wiki/apply_merges.py topics
  python3 tools/wiki/apply_merges.py key-ideas

Reads `wiki/_pending-merges-<facet>.yaml` (Marc edits in place, sets approved: true)
or alternatively `wiki/_approved-merges-<facet>.yaml` if Marc renames it.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
WIKI = REPO / "wiki"
ARCHIVE_BASE = REPO / "archive" / "wiki-merges"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def parse_yaml_minimal(text: str) -> list[dict]:
    """Parse our specific YAML shape without a yaml dep.

    Expected structure:
        merges:
          - confidence: HIGH
            approved: true
            canonical_name: "..."
            canonical_slug: "..."
            reason: "..."
            merge_slugs:
              - slug-a
              - slug-b
            member_names:
              - "name-a"
    """
    out = []
    current = None
    in_list_key = None
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\n")
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if line.startswith("merges:"):
            i += 1
            continue
        if line.startswith("  - "):
            if current is not None:
                out.append(current)
            current = {}
            in_list_key = None
            kv = line[4:].split(":", 1)
            if len(kv) == 2:
                current[kv[0].strip()] = _parse_scalar(kv[1])
            i += 1
            continue
        if line.startswith("    "):
            stripped = line.lstrip(" ")
            if stripped.startswith("- "):
                if in_list_key is not None:
                    current.setdefault(in_list_key, []).append(_parse_scalar(stripped[2:]))
                i += 1
                continue
            if ":" in stripped:
                k, v = stripped.split(":", 1)
                v = v.strip()
                if v == "":
                    in_list_key = k.strip()
                    current[in_list_key] = []
                else:
                    in_list_key = None
                    current[k.strip()] = _parse_scalar(v)
            i += 1
            continue
        i += 1
    if current is not None:
        out.append(current)
    return out


def _parse_scalar(s: str):
    s = s.strip()
    if not s:
        return ""
    # Strip inline YAML comment unless inside quotes
    if not (s.startswith('"') or s.startswith("'")):
        if "#" in s:
            s = s.split("#", 1)[0].strip()
    if s.startswith('"') and s.endswith('"'):
        try:
            import json
            return json.loads(s)
        except Exception:
            return s[1:-1]
    if s == "true":
        return True
    if s == "false":
        return False
    return s


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Returns (frontmatter dict, body)."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
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
    body = text[m.end():]
    return fm, body


def render_frontmatter(fm: dict) -> str:
    out = ["---"]
    for k, v in fm.items():
        if isinstance(v, list):
            out.append(f"{k}:")
            for item in v:
                out.append(f"  - {item}")
        else:
            out.append(f"{k}: {v}")
    out.append("---")
    return "\n".join(out) + "\n"


def union_section(text_a: str, text_b: str, section: str) -> list[str]:
    """Return union of bullet lines under `## section` in both texts."""
    seen = set()
    out = []
    for txt in (text_a, text_b):
        in_section = False
        for line in txt.splitlines():
            if line.strip() == f"## {section}":
                in_section = True
                continue
            if in_section and line.startswith("## "):
                in_section = False
            if in_section and line.strip().startswith("- "):
                if line not in seen:
                    seen.add(line)
                    out.append(line)
    return out


def merge_two_entries(canon_text: str, merge_text: str, merge_name: str) -> str:
    fm_c, body_c = parse_frontmatter(canon_text)
    fm_m, body_m = parse_frontmatter(merge_text)

    # Union aliases
    aliases = list(fm_c.get("aliases", []) or [])
    if merge_name and merge_name not in aliases:
        aliases.append(merge_name)
    for a in fm_m.get("aliases", []) or []:
        if a not in aliases:
            aliases.append(a)
    if aliases:
        fm_c["aliases"] = aliases

    # Sources count
    src_lines = union_section(canon_text, merge_text, "Sources")
    fm_c["sources-count"] = str(len(src_lines))

    # Earliest first-seen, latest last-touched
    if "first-seen" in fm_m:
        if "first-seen" not in fm_c or str(fm_m["first-seen"]) < str(fm_c["first-seen"]):
            fm_c["first-seen"] = fm_m["first-seen"]
    if "last-touched" in fm_m:
        if "last-touched" not in fm_c or str(fm_m["last-touched"]) > str(fm_c["last-touched"]):
            fm_c["last-touched"] = fm_m["last-touched"]

    # Rebuild body: canonical's body, but replace Sources section with the union.
    out_lines = []
    in_sources = False
    inserted = False
    for line in body_c.splitlines():
        if line.strip() == "## Sources":
            in_sources = True
            out_lines.append(line)
            out_lines.append("")
            for s in src_lines:
                out_lines.append(s)
            inserted = True
            continue
        if in_sources:
            if line.startswith("## "):
                in_sources = False
                out_lines.append(line)
            # else skip canonical's Sources lines
            continue
        out_lines.append(line)
    if not inserted:
        out_lines.append("")
        out_lines.append("## Sources")
        out_lines.append("")
        out_lines.extend(src_lines)

    return render_frontmatter(fm_c) + "\n".join(out_lines).strip("\n") + "\n"


def relink_wiki(merge_slug: str, canonical_slug: str, facet: str) -> int:
    """Replace [[<facet>/merge_slug]] (and [[merge_slug]] in same facet's
    sibling entries) with canonical. Returns number of files updated."""
    count = 0
    for p in WIKI.rglob("*.md"):
        if p.name in ("INDEX.md",):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        original = text
        text = re.sub(rf"\[\[{re.escape(facet)}/{re.escape(merge_slug)}(\|[^\]]*|#[^\]]*)?\]\]",
                      f"[[{facet}/{canonical_slug}]]", text)
        text = re.sub(rf"\[\[{re.escape(merge_slug)}(\|[^\]]*|#[^\]]*)?\]\]",
                      f"[[{canonical_slug}]]", text)
        if text != original:
            p.write_text(text, encoding="utf-8")
            count += 1
    return count


def archive_entry(facet: str, slug: str, archive_dir: Path) -> None:
    src = WIKI / facet / f"{slug}.md"
    if not src.exists():
        return
    dst_dir = archive_dir / facet
    dst_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst_dir / f"{slug}.md"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("facet", choices=["persons", "topics", "key-ideas"])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--input", default=None,
                    help="path to YAML; defaults to wiki/_approved-merges-<facet>.yaml "
                         "with fallback to wiki/_pending-merges-<facet>.yaml")
    args = ap.parse_args()

    facet = args.facet
    if args.input:
        yaml_path = Path(args.input)
    else:
        yaml_path = WIKI / f"_approved-merges-{facet}.yaml"
        if not yaml_path.exists():
            yaml_path = WIKI / f"_pending-merges-{facet}.yaml"

    if not yaml_path.exists():
        print(f"ERROR: {yaml_path} not found. Run propose_merges.py first.", file=sys.stderr)
        sys.exit(1)

    text = yaml_path.read_text(encoding="utf-8")
    merges = parse_yaml_minimal(text)
    approved = [m for m in merges if m.get("approved") is True]
    skipped = [m for m in merges if m.get("approved") is not True]
    print(f"loaded {len(merges)} merges; {len(approved)} approved, {len(skipped)} skipped")

    if not approved:
        print("nothing approved; nothing to apply.")
        return

    archive_dir = ARCHIVE_BASE / date.today().isoformat()
    if not args.dry_run:
        archive_dir.mkdir(parents=True, exist_ok=True)

    applied = 0
    for m in approved:
        canon_slug = m["canonical_slug"]
        canon_name = m["canonical_name"]
        merge_slugs = list(m.get("merge_slugs", []))
        member_names = list(m.get("member_names", []))
        canon_path = WIKI / facet / f"{canon_slug}.md"

        # If canonical is one of the existing entries, use it; otherwise pick the
        # first existing slug as the seed.
        if not canon_path.exists():
            seed = None
            for s in [canon_slug] + merge_slugs:
                p = WIKI / facet / f"{s}.md"
                if p.exists():
                    seed = p; break
            if seed is None:
                print(f"  skip: no existing entry for {canon_slug} or any of {merge_slugs}")
                continue
            if seed != canon_path:
                if args.dry_run:
                    print(f"  [dry] would rename {seed.name} → {canon_slug}.md")
                else:
                    seed.rename(canon_path)

        # Make sure name in canonical frontmatter is the chosen canonical_name.
        canon_text = canon_path.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(canon_text)
        fm["name"] = canon_name
        fm["slug"] = canon_slug
        canon_text = render_frontmatter(fm) + body

        # Merge each member into canonical
        for m_slug in merge_slugs:
            mp = WIKI / facet / f"{m_slug}.md"
            if not mp.exists():
                continue
            try:
                m_text = mp.read_text(encoding="utf-8")
                m_fm, _ = parse_frontmatter(m_text)
                m_name = m_fm.get("name", m_slug)
            except Exception:
                m_text = ""; m_name = m_slug
            canon_text = merge_two_entries(canon_text, m_text, m_name)

            if args.dry_run:
                print(f"  [dry] would archive {facet}/{m_slug}.md → archive/wiki-merges/{date.today().isoformat()}/{facet}/")
            else:
                archive_entry(facet, m_slug, archive_dir)

        if args.dry_run:
            print(f"  [dry] would write canonical {facet}/{canon_slug}.md (after merging {len(merge_slugs)} entries)")
        else:
            canon_path.write_text(canon_text, encoding="utf-8")
            for m_slug in merge_slugs:
                relink_wiki(m_slug, canon_slug, facet)

        applied += 1

    print(f"\napplied: {applied}/{len(approved)}")
    if args.dry_run:
        print("(dry run — no changes written)")


if __name__ == "__main__":
    main()
