#!/usr/bin/env python3
"""tools/wiki/render_merge_walkthrough.py — navigable merge validation chain.

Reads `wiki/_pending-merges-<facet>.yaml` for persons, topics, key-ideas.
Outputs a single `wiki/MERGE-WALKTHROUGH.md` with one clickable section per
cluster — Marc walks point by point in Obsidian.

Each cluster shows:
  - canonical name + slug
  - confidence + reason
  - member entries as wikilinks (click to open)
  - sample shared source files (click to verify)
  - top co-occurring topics + key-ideas (context)
  - the YAML line key to flip (`approved: true|false`)

Re-runnable. Idempotent.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

REPO = Path(__file__).resolve().parent.parent.parent
WIKI = REPO / "wiki"

FACETS = ["persons", "topics", "key-ideas"]
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apply_merges import parse_yaml_minimal


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


def parse_section(text: str, header: str) -> list[str]:
    in_section = False
    out = []
    for line in text.splitlines():
        if line.strip() == f"## {header}":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.strip().startswith("- "):
            out.append(line.strip()[2:])
    return out


def parse_subsection(text: str, header: str, sub: str) -> list[str]:
    """Parse a `**Sub**` subsection inside `## header`."""
    in_section = False
    in_sub = False
    out = []
    for line in text.splitlines():
        if line.strip() == f"## {header}":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.strip() == f"**{sub}**":
            in_sub = True
            continue
        if in_sub and line.strip().startswith("**") and line.strip().endswith("**"):
            in_sub = False
        if in_sub and line.strip().startswith("- "):
            out.append(line.strip()[2:])
    return out


def load_entry(facet: str, slug: str) -> dict | None:
    p = WIKI / facet / f"{slug}.md"
    if not p.exists():
        return None
    text = p.read_text(encoding="utf-8", errors="ignore")
    fm = parse_frontmatter(text)
    sources = []
    summary_first = ""
    in_summary = False
    in_sources = False
    for line in text.splitlines():
        if line.strip() == "## Summary":
            in_summary = True; continue
        if in_summary and line.startswith("## "):
            in_summary = False
        if in_summary and line.strip() and not summary_first:
            summary_first = line.strip()
        if line.strip() == "## Sources":
            in_sources = True; continue
        if in_sources and line.startswith("## "):
            in_sources = False
        if in_sources and line.strip().startswith("- [["):
            m = re.search(r"\[\[([^\]\|\#]+)\]\]", line)
            if m: sources.append(m.group(1).strip())
    # Co-occurrence
    if facet == "persons":
        topics = parse_subsection(text, "Co-occurrence", "Topics")
        ideas = parse_subsection(text, "Co-occurrence", "Key ideas")
    else:
        topics = []
        ideas = []
    return {
        "name": fm.get("name", slug).strip('"').strip("'"),
        "summary": summary_first,
        "sources": sources,
        "topics": topics,
        "ideas": ideas,
    }


def render_cluster(facet: str, idx: int, cluster: dict) -> list[str]:
    confidence = cluster.get("confidence", "?")
    canon_name = cluster.get("canonical_name", "?")
    canon_slug = cluster.get("canonical_slug", "?")
    reason = cluster.get("reason", "")
    merge_slugs = cluster.get("merge_slugs") or []

    # All slugs in cluster: canonical (if exists as entry) + merges
    all_slugs = [canon_slug] + [s for s in merge_slugs if s != canon_slug]

    member_entries = []
    for s in all_slugs:
        e = load_entry(facet, s)
        if e:
            member_entries.append((s, e))

    # Shared sources (intersection of source lists across members that exist)
    if member_entries:
        sets = [set(e[1]["sources"]) for e in member_entries]
        shared_sources = set.intersection(*sets) if sets else set()
        union_sources = set.union(*sets) if sets else set()
    else:
        shared_sources = set()
        union_sources = set()

    out = []
    out.append(f"### #{idx} — `{canon_slug}` · **{canon_name}** · {confidence}")
    out.append("")
    out.append(f"*{reason}* · members: {len(member_entries)} · shared sources: {len(shared_sources)} · union sources: {len(union_sources)}")
    out.append("")
    out.append("**Members** (click to open):")
    out.append("")
    if not member_entries:
        out.append(f"- *(no entries on disk for any of: {', '.join(all_slugs)})*")
    for s, e in member_entries:
        marker = " ◀ canonical" if s == canon_slug else ""
        ctx = f" — {e['summary']}" if e["summary"] and not e["summary"].startswith("*[") else ""
        out.append(f"- [[wiki/{facet}/{s}|{s}]] · *{e['name']}* ({len(e['sources'])} src){marker}{ctx}")
    out.append("")

    if shared_sources:
        out.append(f"**Shared sources** ({len(shared_sources)}):")
        out.append("")
        for src in sorted(shared_sources)[:8]:
            out.append(f"- [[{src}]]")
        if len(shared_sources) > 8:
            out.append(f"- *...+{len(shared_sources) - 8} more (see members for full lists)*")
        out.append("")

    if facet == "persons" and member_entries:
        # Top co-occurring topics + key-ideas across the cluster
        topic_count: dict[str, int] = defaultdict(int)
        idea_count: dict[str, int] = defaultdict(int)
        for _, e in member_entries:
            for t in e["topics"]:
                # parse "[[topics/x]] (n)"
                m = re.search(r"\[\[topics/([^\]\|\#]+)\]\]", t)
                if m:
                    topic_count[m.group(1)] += 1
            for i in e["ideas"]:
                m = re.search(r"\[\[key-ideas/([^\]\|\#]+)\]\]", i)
                if m:
                    idea_count[m.group(1)] += 1
        top_topics = sorted(topic_count.items(), key=lambda x: -x[1])[:6]
        top_ideas = sorted(idea_count.items(), key=lambda x: -x[1])[:6]
        if top_topics:
            out.append("**Top co-occurring topics:** " + " · ".join(f"[[wiki/topics/{t}|{t}]]" for t, _ in top_topics))
            out.append("")
        if top_ideas:
            out.append("**Top co-occurring key-ideas:** " + " · ".join(f"[[wiki/key-ideas/{i}|{i}]]" for i, _ in top_ideas))
            out.append("")

    approved = cluster.get("approved")
    state = "✅ approved (will apply)" if approved is True else "⏸ NOT approved (will skip)"
    out.append(f"**State:** {state}")
    out.append(f"**To flip:** open [[wiki/_pending-merges-{facet}.yaml]] and set `approved: true|false` for the entry whose `canonical_slug: {canon_slug}`.")
    out.append("")
    out.append("---")
    out.append("")
    return out


def render_facet(facet: str) -> tuple[str, dict]:
    yaml_path = WIKI / f"_pending-merges-{facet}.yaml"
    if not yaml_path.exists():
        return "", {}
    text = yaml_path.read_text(encoding="utf-8")
    clusters = parse_yaml_minimal(text)

    by_conf = {"HIGH": [], "MED": [], "LOW": []}
    for c in clusters:
        by_conf.setdefault(c.get("confidence", "?"), []).append(c)

    counts = {k: len(v) for k, v in by_conf.items() if v}

    sections = []
    sections.append(f"## {facet} — {len(clusters)} clusters")
    sections.append("")
    sections.append(f"YAML to edit: [[wiki/_pending-merges-{facet}.yaml]] · MD detail: [[wiki/_pending-merges-{facet}|_pending-merges-{facet}]]")
    sections.append("")
    bullets = " · ".join(f"{k}: {len(v)}" for k, v in by_conf.items() if v)
    sections.append(f"**Confidence breakdown:** {bullets}")
    sections.append("")

    idx = 1
    for level in ("HIGH", "MED", "LOW"):
        if not by_conf[level]:
            continue
        sections.append(f"### {level} — {len(by_conf[level])} clusters")
        sections.append("")
        for c in by_conf[level]:
            sections.extend(render_cluster(facet, idx, c))
            idx += 1
    return "\n".join(sections), counts


def main():
    out = []
    out.append("# Wiki merge — validation walkthrough")
    out.append("")
    out.append(f"Generated by `tools/wiki/render_merge_walkthrough.py` at {datetime.now().isoformat(timespec='seconds')}.")
    out.append("")
    out.append("**How to use this:**")
    out.append("")
    out.append("1. Walk top-to-bottom. Each cluster has clickable wikilinks to its members and shared sources — click to verify, come back here, decide.")
    out.append("2. To **approve** a cluster, open the relevant `_pending-merges-<facet>.yaml` (linked at the top of each facet section), find the entry whose `canonical_slug:` matches, set `approved: true`.")
    out.append("3. To **amend a cluster** (wrong canonical, drop a member, etc.), edit the YAML directly. Save.")
    out.append("4. To **reject**, leave `approved: false` (default for MED/LOW).")
    out.append("5. When done with a facet, run `python3 tools/wiki/apply_merges.py <facet> --dry-run` to preview, then drop `--dry-run`. Then re-run `tools/wiki/build_cooccurrence.py` and `tools/wiki/render_indexes.py` to refresh.")
    out.append("")
    out.append("Strict-confidence policy: HIGH defaults to `approved: true`. MED + LOW default to `approved: false` — your call per row.")
    out.append("")

    out.append("## Table of contents")
    out.append("")
    counts_summary = []
    for facet in FACETS:
        out.append(f"- [[#{facet} — ]]")
    out.append("")
    out.append("---")
    out.append("")

    grand = {"HIGH": 0, "MED": 0, "LOW": 0}
    for facet in FACETS:
        body, counts = render_facet(facet)
        if not body:
            continue
        out.append(body)
        for k, v in counts.items():
            grand[k] = grand.get(k, 0) + v

    out.append("---")
    out.append("")
    out.append("## Summary")
    out.append("")
    out.append(f"- **Total HIGH (auto-apply default):** {grand['HIGH']}")
    out.append(f"- **Total MED (review needed):** {grand['MED']}")
    out.append(f"- **Total LOW (review needed):** {grand['LOW']}")
    out.append(f"- **Grand total clusters:** {sum(grand.values())}")
    out.append("")
    out.append("After approving and applying merges:")
    out.append("")
    out.append("```bash")
    out.append("python3 tools/wiki/apply_merges.py persons --dry-run    # preview")
    out.append("python3 tools/wiki/apply_merges.py persons               # apply")
    out.append("python3 tools/wiki/build_cooccurrence.py                # refresh links")
    out.append("python3 tools/wiki/render_indexes.py                    # refresh indexes")
    out.append("python3 tools/wiki/render_merge_walkthrough.py          # refresh this file")
    out.append("```")
    out.append("")

    target = WIKI / "MERGE-WALKTHROUGH.md"
    target.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {target}")


if __name__ == "__main__":
    main()
