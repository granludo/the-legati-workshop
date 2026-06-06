#!/usr/bin/env python3
"""tools/wiki/build_cooccurrence.py — augment wiki entries with co-occurrence sections.

Walks the bootstrap cache (tools/wiki/cache/*.json) — each cached entry is
the per-file analysis with persons + topics + key_ideas. From this, we build:

  (person, topic) → list of source files where both appear
  (person, key_idea) → ditto
  (topic, key_idea) → ditto

Then for each wiki entry, append/replace a `## Co-occurrence` section listing
top-N related items.

Re-runnable any time. Idempotent: replaces existing Co-occurrence sections.
Uses the SAME slugify rule the bootstrap used so we stay aligned with entry
filenames.

Usage:
  python3 tools/wiki/build_cooccurrence.py            # all facets
  python3 tools/wiki/build_cooccurrence.py --top 15
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
WIKI = REPO / "wiki"
CACHE = REPO / "tools" / "wiki" / "cache"

SKIP_PERSON_NAMES = {
    "marc", "marc alier", "marc alier forment", "ludo",
    "agatha", "nagatha", "nagatha christie",
    "mycroft", "mycroft holmes",
    "bilby",
}


def slugify(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def load_cache() -> list[dict]:
    out = []
    for f in CACHE.glob("*.json"):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            if isinstance(d, dict):
                out.append(d)
        except Exception:
            continue
    return out


FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def build_alias_map(facet: str) -> dict[str, str]:
    """For each entry in wiki/<facet>/, map every alias-slug → canonical-slug.

    Reads `aliases:` from frontmatter. Allows the co-occurrence builder to
    resolve cache mentions (which use raw, pre-merge slugs) onto whichever
    canonical entry currently exists.
    """
    out: dict[str, str] = {}
    facet_dir = WIKI / facet
    if not facet_dir.exists():
        return out
    for p in facet_dir.glob("*.md"):
        if p.name == "INDEX.md":
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        m = FM_RE.match(text)
        if not m:
            continue
        canonical = p.stem
        out[canonical] = canonical
        in_aliases = False
        for line in m.group(1).splitlines():
            if line.startswith("aliases:"):
                in_aliases = True
                continue
            if in_aliases:
                if line.startswith("  - "):
                    alias = line[4:].strip().strip('"').strip("'")
                    if alias:
                        out[slugify(alias)] = canonical
                else:
                    in_aliases = False
    return out


def build_indices(cache: list[dict], person_map: dict[str, str],
                   topic_map: dict[str, str], idea_map: dict[str, str]):
    """Build co-occurrence indices.

    Each cache entry has been analyzed from one file. The file path isn't
    stored in the cache JSON — we infer co-occurrence at the per-cache-record
    level (since each record == one file's analysis). For source-file
    grounding, the wiki entries already carry the source paths; here we just
    care about which-slug-co-occurs-with-which-slug.
    """
    # For each cache record, get its slug-sets
    person_topic = defaultdict(int)
    person_idea = defaultdict(int)
    topic_idea = defaultdict(int)

    person_seen_in = defaultdict(int)
    topic_seen_in = defaultdict(int)
    idea_seen_in = defaultdict(int)

    for rec in cache:
        persons = []
        for p in rec.get("persons_mentioned") or []:
            n = (p.get("name") or "").strip()
            if not n or n.lower() in SKIP_PERSON_NAMES:
                continue
            sl = slugify(n)
            if sl:
                # resolve through alias map; fall back to raw slug if not mapped
                persons.append(person_map.get(sl, sl))
        topics = [topic_map.get(slugify(t.strip()), slugify(t.strip()))
                  for t in (rec.get("topics") or []) if isinstance(t, str) and t.strip()]
        ideas  = [idea_map.get(slugify(k.strip()), slugify(k.strip()))
                  for k in (rec.get("key_ideas") or []) if isinstance(k, str) and k.strip()]
        topics = [t for t in topics if t]
        ideas  = [i for i in ideas if i]

        for p in set(persons):
            person_seen_in[p] += 1
        for t in set(topics):
            topic_seen_in[t] += 1
        for i in set(ideas):
            idea_seen_in[i] += 1

        for p in set(persons):
            for t in set(topics):
                person_topic[(p, t)] += 1
            for i in set(ideas):
                person_idea[(p, i)] += 1
        for t in set(topics):
            for i in set(ideas):
                topic_idea[(t, i)] += 1

    return {
        "person_topic": dict(person_topic),
        "person_idea": dict(person_idea),
        "topic_idea": dict(topic_idea),
        "person_seen_in": dict(person_seen_in),
        "topic_seen_in": dict(topic_seen_in),
        "idea_seen_in": dict(idea_seen_in),
    }


def top_by_score(pairs: dict, key_index: int, query: str, top: int) -> list[tuple[str, int]]:
    """For a (a, b) → count dict, return top-N b items where a == query, sorted by count desc."""
    out = []
    for (a, b), c in pairs.items():
        if [a, b][key_index] == query:
            other = [a, b][1 - key_index]
            out.append((other, c))
    out.sort(key=lambda x: (-x[1], x[0]))
    return out[:top]


COOCCUR_HEADING = "## Co-occurrence"


def upsert_cooccur(text: str, body: str) -> str:
    """Replace existing Co-occurrence section, or append a new one."""
    lines = text.splitlines()
    out_lines = []
    in_section = False
    section_replaced = False
    for line in lines:
        if line.strip() == COOCCUR_HEADING:
            in_section = True
            section_replaced = True
            out_lines.append(COOCCUR_HEADING)
            out_lines.append("")
            for bl in body.splitlines():
                out_lines.append(bl)
            out_lines.append("")
            continue
        if in_section:
            if line.startswith("## "):
                in_section = False
                out_lines.append(line)
            # else skip old section content
        else:
            out_lines.append(line)
    if not section_replaced:
        if out_lines and out_lines[-1].strip() != "":
            out_lines.append("")
        out_lines.append(COOCCUR_HEADING)
        out_lines.append("")
        for bl in body.splitlines():
            out_lines.append(bl)
        out_lines.append("")
    return "\n".join(out_lines).rstrip("\n") + "\n"


def render_cooccur_for(facet: str, slug: str, indices: dict, top: int) -> str:
    parts = []
    if facet == "persons":
        topics = top_by_score(indices["person_topic"], 0, slug, top)
        ideas = top_by_score(indices["person_idea"], 0, slug, top)
        if topics:
            parts.append("**Topics**")
            parts.append("")
            for t, c in topics:
                parts.append(f"- [[topics/{t}]] ({c})")
            parts.append("")
        if ideas:
            parts.append("**Key ideas**")
            parts.append("")
            for i, c in ideas:
                parts.append(f"- [[key-ideas/{i}]] ({c})")
    elif facet == "topics":
        persons = top_by_score(indices["person_topic"], 1, slug, top)
        ideas = top_by_score(indices["topic_idea"], 0, slug, top)
        if persons:
            parts.append("**Key persons**")
            parts.append("")
            for p, c in persons:
                parts.append(f"- [[persons/{p}]] ({c})")
            parts.append("")
        if ideas:
            parts.append("**Related key-ideas**")
            parts.append("")
            for i, c in ideas:
                parts.append(f"- [[key-ideas/{i}]] ({c})")
    elif facet == "key-ideas":
        persons = top_by_score(indices["person_idea"], 1, slug, top)
        topics = top_by_score(indices["topic_idea"], 1, slug, top)
        if persons:
            parts.append("**Key persons**")
            parts.append("")
            for p, c in persons:
                parts.append(f"- [[persons/{p}]] ({c})")
            parts.append("")
        if topics:
            parts.append("**Topics**")
            parts.append("")
            for t, c in topics:
                parts.append(f"- [[topics/{t}]] ({c})")
    return "\n".join(parts).strip("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=10, help="top-N items per section")
    args = ap.parse_args()

    cache = load_cache()
    print(f"loaded {len(cache)} cache records")
    person_map = build_alias_map("persons")
    topic_map = build_alias_map("topics")
    idea_map = build_alias_map("key-ideas")
    print(f"alias maps: persons={len(person_map)}, topics={len(topic_map)}, key-ideas={len(idea_map)}")
    indices = build_indices(cache, person_map, topic_map, idea_map)
    print(f"unique slugs: persons={len(indices['person_seen_in'])}, "
          f"topics={len(indices['topic_seen_in'])}, "
          f"key-ideas={len(indices['idea_seen_in'])}")

    updated = {"persons": 0, "topics": 0, "key-ideas": 0}
    for facet in ("persons", "topics", "key-ideas"):
        facet_dir = WIKI / facet
        if not facet_dir.exists():
            continue
        for p in facet_dir.glob("*.md"):
            if p.name in ("INDEX.md",):
                continue
            slug = p.stem
            body = render_cooccur_for(facet, slug, indices, args.top)
            if not body:
                continue
            text = p.read_text(encoding="utf-8")
            new_text = upsert_cooccur(text, body)
            if new_text != text:
                p.write_text(new_text, encoding="utf-8")
                updated[facet] += 1

    print(f"updated entries: {updated}")


if __name__ == "__main__":
    main()
