#!/usr/bin/env python3
"""tools/wiki/propose_merges.py — generate merge-candidate proposals for a facet.

Walks wiki/<facet>/*.md, clusters entries that look like aliases of the same
underlying thing, scores each cluster, writes:

  wiki/_pending-merges-<facet>.md     # human-readable triage view
  wiki/_pending-merges-<facet>.yaml   # machine-readable (Marc edits to approve)

Heuristics for clustering:
  1. Diacritic-folded slug match (Garcia-Penalvo == García-Peñalvo)
  2. Token-overlap fuzzy match (Levenshtein-1 on each token)
  3. Initial-vs-full match (M. Alier ↔ Marc Alier)
  4. Known aliases loaded from memory/feedback_*alias*.md and similar (auto-applied)

Confidence levels:
  HIGH — known alias from memory, OR diacritic-fold + ≥1 shared source
  MED  — fuzzy match + shared topics, OR diacritic-fold with 0 shared sources
  LOW  — first-name-only match, ambiguous initials, no shared sources

Marc reviews the .md, edits the .yaml to approve / reject / amend, then runs
apply_merges.py.

Usage:
  python3 tools/wiki/propose_merges.py persons
  python3 tools/wiki/propose_merges.py topics
  python3 tools/wiki/propose_merges.py key-ideas
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
MEMORY = REPO / "memory"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
LIST_ITEM_RE = re.compile(r"^- \[\[([^\]\|\#]+)\]\](?: — (.+))?$", re.MULTILINE)


def slugify(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(cur[-1] + 1, prev[j] + 1, prev[j-1] + (ca != cb)))
        prev = cur
    return prev[-1]


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    out = {}
    current_list_key = None
    for line in m.group(1).splitlines():
        if line.startswith("  -") and current_list_key:
            out.setdefault(current_list_key, []).append(line[3:].strip())
            continue
        current_list_key = None
        if ":" in line:
            k, v = line.split(":", 1)
            v = v.strip()
            if v == "":
                current_list_key = k.strip()
                out[k.strip()] = []
            else:
                out[k.strip()] = v
    return out


def parse_sources(text: str) -> list[str]:
    """Extract the Sources section's wikilink targets."""
    in_sources = False
    out = []
    for line in text.splitlines():
        if line.strip().startswith("## Sources"):
            in_sources = True
            continue
        if in_sources and line.startswith("## "):
            break
        if in_sources:
            m = re.search(r"\[\[([^\]\|\#]+)\]\]", line)
            if m:
                out.append(m.group(1).strip())
    return out


def parse_summary_line(text: str) -> str:
    """First non-empty line of the Summary section."""
    in_summary = False
    for line in text.splitlines():
        if line.strip().startswith("## Summary"):
            in_summary = True
            continue
        if in_summary and line.startswith("## "):
            break
        if in_summary and line.strip():
            return line.strip()
    return ""


# Hand-curated aliases — known-correct, derived from memory files but parsed safely.
# Format: (canonical_name, [variants]). Add new entries as they accrete.
KNOWN_ALIASES_PERSONS: list[tuple[str, list[str]]] = [
    ("Marc Alier",
        ["Marc Alier Forment", "M. Alier", "M Alier", "Ludo", "granludo",
         "Marc Alier-Forment", "Alier", "Alier Forment Marc"]),
    ("Francisco García-Peñalvo",
        ["Fran", "FGP", "F. García-Peñalvo", "F. J. García-Peñalvo",
         "F.J. García-Peñalvo", "Francisco J. García-Peñalvo",
         "García-Peñalvo", "Garcia-Penalvo", "García Peñalvo",
         "Francisco García Peñalvo", "FJ García-Peñalvo", "F García-Peñalvo"]),
    ("Maria José Casañ",
        ["Sé", "María José Casañ", "Maria Jose Casany", "M. J. Casany",
         "Maria J. Casany", "MJ Casany", "Casañ", "Casany",
         "Maria-José Casañ", "M.J. Casañ", "Casany Guerrero",
         "Maria José Casany Guerrero", "Casañ Guerrero",
         "M. J. Casan", "Casan", "M. J. Casan-Guerrero", "Casan-Guerrero"]),
    ("Faraón Llorens Largo",
        ["Faraón Llorens", "Faraon Llorens", "Faraon Llorens Largo",
         "Llorens Largo", "F. Llorens", "F. Llorens Largo", "Llorens"]),
    ("Juan Andrés Pereira",
        ["Juanan", "Juan Andrés Pereira Varela", "J. A. Pereira",
         "JA Pereira", "J. Pereira", "Pereira Varela",
         "Juan-Antonio Pereira-Varela", "Juan Antonio Pereira Varela",
         "Juan Antonio Pereira"]),
    ("Daniel Amo Filvà",
        ["Daniel Amo", "D. Amo", "Amo Filvà", "Amo Filva", "Amo, D.",
         "D Amo", "Amo D"]),
    ("Xabi Ezpeleta",
        ["Xavi Peleta", "Xavier Peleta", "Xabi Ezpeleta", "Xavier Ezpeleta"]),  # Marc 2026-05-10
    ("Miguel Ángel Conde",
        ["Miguel Angel Conde", "Miguel A. Conde", "M.A. Conde", "MA Conde",
         "Miguel Angel Conde Gonzalez", "Miguel Ángel Conde González"]),
    ("Steve Jobs", ["Jobs"]),
    ("Steve Wozniak", ["Wozniak", "Woz"]),
    ("Nicholas Negroponte", ["Negroponte"]),
    ("Seymour Papert", ["Papert"]),
    ("B. F. Skinner", ["BF Skinner", "B.F. Skinner", "Skinner"]),
    ("Richard Stallman", ["Stallman", "RMS"]),
    ("Yuval Noah Harari", ["Harari", "Y. N. Harari", "Y.N. Harari"]),
    ("Cory Doctorow", ["Doctorow"]),
    ("Shoshana Zuboff", ["Zuboff"]),
    ("Neal Stephenson", ["Stephenson"]),
    ("J. R. R. Tolkien", ["JRR Tolkien", "Tolkien"]),
    ("Isaac Asimov", ["Asimov"]),
    ("Craig Alanson", ["Alanson"]),
]


def load_known_aliases() -> list[tuple[str, list[str]]]:
    """Return the hand-curated alias list. Hand-curated rather than parsed
    because the natural-language descriptions in memory/user_*alias*.md vary
    too much to regex reliably. New aliases get added to KNOWN_ALIASES_PERSONS
    above when discovered. The memory files remain authoritative for *why*."""
    return list(KNOWN_ALIASES_PERSONS)


def normalize_name(name: str) -> str:
    """Lowercase, strip diacritics, collapse whitespace, sort tokens."""
    n = unicodedata.normalize("NFKD", name)
    n = n.encode("ascii", "ignore").decode("ascii")
    n = n.lower()
    n = re.sub(r"[^\w\s-]", " ", n)
    n = re.sub(r"\s+", " ", n).strip()
    return n


def tokenize_name(name: str) -> list[str]:
    norm = normalize_name(name)
    return [t for t in norm.replace("-", " ").split() if t]


def is_initial_form(short: str, full: str) -> bool:
    """Return True if `short` looks like an initialed form of `full`."""
    s_tokens = tokenize_name(short)
    f_tokens = tokenize_name(full)
    if len(s_tokens) > len(f_tokens):
        return False
    for st, ft in zip(s_tokens, f_tokens):
        if st == ft:
            continue
        # Initial form: "m" matches "marc", "m." matches "marc"
        st_clean = st.rstrip(".")
        if len(st_clean) == 1 and ft.startswith(st_clean):
            continue
        return False
    return True


def fuzzy_match_tokens(a: list[str], b: list[str]) -> bool:
    """Return True iff (1) the *longest* token in `a` fuzzy-matches the
    longest token in `b` (Levenshtein ≤ 1), AND (2) for short names (≤2
    tokens) ALL non-trivial tokens fuzzy-match. Tokens of length ≤1 don't
    count as matches by themselves (they're initials, ambiguous).

    This rejects clusters like ["a-alier", "a-bandura"] which used to match
    on the leading "a" alone, producing 250-member junk clusters.
    """
    if not a or not b:
        return False
    # Longest-token match (last name, usually)
    a_long = max(a, key=len)
    b_long = max(b, key=len)
    if len(a_long) <= 1 or len(b_long) <= 1:
        return False
    if levenshtein(a_long, b_long) > 1:
        return False
    # Require ALL non-trivial tokens of the *shorter* name to fuzzy-match
    # against tokens of the longer name. This kills the same-surname-different-
    # people pattern (e.g., antoni-hernandez-fernandez ↔ agustin-fernandez:
    # only "fernandez" matches; "agustin" vs "antoni"/"hernandez" doesn't).
    short, long = (a, b) if len(a) <= len(b) else (b, a)
    short_real = [t for t in short if len(t) > 1]
    long_real = [t for t in long if len(t) > 1]
    if not short_real or not long_real:
        return False
    for ta in short_real:
        if not any(levenshtein(ta, tb) <= 1 for tb in long_real):
            return False
    return True


def cluster_entries(entries: list[dict],
                    known_aliases: list[tuple[str, list[str]]]) -> list[dict]:
    """Build candidate clusters across `entries`. Each entry is a dict with
    keys: slug, name, normalized, sources (set), contexts (list)."""
    clusters: list[dict] = []
    used: set[str] = set()

    # Pass 1: known aliases (auto-HIGH, deterministic)
    for canonical, variants in known_aliases:
        canon_slug = slugify(canonical)
        canon_normalized = normalize_name(canonical)
        candidates = []
        seen_slugs = set()
        # Build the full set of acceptable slugs/normalized for this canonical
        accept_slugs = {canon_slug} | {slugify(v) for v in variants}
        accept_norms = {canon_normalized} | {normalize_name(v) for v in variants}
        for e in entries:
            if e["slug"] in used or e["slug"] in seen_slugs:
                continue
            if e["slug"] in accept_slugs or e["normalized"] in accept_norms:
                candidates.append(e)
                seen_slugs.add(e["slug"])
        if len(candidates) >= 2:
            for c in candidates:
                used.add(c["slug"])
            clusters.append({
                "confidence": "HIGH",
                "canonical_name": canonical,
                "canonical_slug": canon_slug,
                "members": candidates,
                "reason": "known alias from memory",
            })

    # Pass 2: diacritic-fold matches
    by_normalized: dict[str, list[dict]] = defaultdict(list)
    for e in entries:
        if e["slug"] in used:
            continue
        by_normalized[e["normalized"]].append(e)
    for norm, members in by_normalized.items():
        if len(members) < 2:
            continue
        for m in members:
            used.add(m["slug"])
        # Pick canonical: longest name (most info), prefer one with diacritics if any.
        canonical = max(members, key=lambda m: (sum(1 for c in m["name"] if not c.isascii()), len(m["name"])))
        shared_sources = set.intersection(*(m["sources"] for m in members))
        confidence = "HIGH" if shared_sources else "MED"
        clusters.append({
            "confidence": confidence,
            "canonical_name": canonical["name"],
            "canonical_slug": slugify(canonical["name"]),
            "members": members,
            "reason": f"diacritic/case-fold match, {len(shared_sources)} shared sources",
        })

    # Pass 3: token-fuzzy and initial-vs-full
    remaining = [e for e in entries if e["slug"] not in used]
    for i, ea in enumerate(remaining):
        if ea["slug"] in used:
            continue
        ea_tokens = tokenize_name(ea["name"])
        if not ea_tokens:
            continue
        cluster_members = [ea]
        for eb in remaining[i+1:]:
            if eb["slug"] in used or eb["slug"] == ea["slug"]:
                continue
            eb_tokens = tokenize_name(eb["name"])
            if not eb_tokens:
                continue
            # Initial-vs-full
            if is_initial_form(ea["name"], eb["name"]) or is_initial_form(eb["name"], ea["name"]):
                cluster_members.append(eb); continue
            # Fuzzy token match (need at least 2 tokens for confidence)
            if len(ea_tokens) >= 2 and len(eb_tokens) >= 2 and fuzzy_match_tokens(ea_tokens, eb_tokens):
                cluster_members.append(eb); continue
        if len(cluster_members) < 2:
            continue
        for c in cluster_members:
            used.add(c["slug"])
        canonical = max(cluster_members, key=lambda m: len(m["name"]))
        shared_sources = set.intersection(*(m["sources"] for m in cluster_members))
        # Confidence:
        #  - shared_sources >= 2 → MED
        #  - shared_sources == 0 → LOW
        if len(shared_sources) >= 2:
            confidence = "MED"
        elif len(shared_sources) == 1:
            confidence = "MED"
        else:
            confidence = "LOW"
        clusters.append({
            "confidence": confidence,
            "canonical_name": canonical["name"],
            "canonical_slug": slugify(canonical["name"]),
            "members": cluster_members,
            "reason": f"fuzzy/initial match, {len(shared_sources)} shared sources",
        })

    return clusters


def render_md(facet: str, clusters: list[dict]) -> str:
    lines = [
        f"# Pending merges — {facet}",
        "",
        f"Generated by `tools/wiki/propose_merges.py {facet}`. Strict-confidence policy: only **HIGH** clusters auto-apply when Marc runs `apply_merges.py`. **MED** and **LOW** require explicit approval in the YAML.",
        "",
        f"To approve: edit `wiki/_pending-merges-{facet}.yaml`. Set `approved: true` on a cluster (or remove `approved: false`) and run `apply_merges.py {facet}`.",
        "",
        "## Counts",
        "",
        f"- HIGH: {sum(1 for c in clusters if c['confidence']=='HIGH')}",
        f"- MED:  {sum(1 for c in clusters if c['confidence']=='MED')}",
        f"- LOW:  {sum(1 for c in clusters if c['confidence']=='LOW')}",
        "",
    ]
    for level in ("HIGH", "MED", "LOW"):
        sub = [c for c in clusters if c["confidence"] == level]
        if not sub:
            continue
        lines.append(f"## {level} ({len(sub)})")
        lines.append("")
        lines.append("| Canonical (proposed) | Members | Shared srcs | Reason |")
        lines.append("|---|---|---|---|")
        for c in sub:
            members_str = ", ".join(f"`{m['slug']}`" for m in c["members"])
            shared = set.intersection(*(m["sources"] for m in c["members"]))
            lines.append(f"| **{c['canonical_name']}** (`{c['canonical_slug']}`) | {members_str} | {len(shared)} | {c['reason']} |")
        lines.append("")
    return "\n".join(lines) + "\n"


def render_yaml(facet: str, clusters: list[dict]) -> str:
    lines = [
        f"# Pending merges — {facet}",
        f"# Generated by tools/wiki/propose_merges.py {facet}.",
        f"# To approve a cluster: set `approved: true` (HIGH defaults to true; MED/LOW default to false).",
        f"# To override the canonical: edit `canonical_slug` and `canonical_name`.",
        f"# To exclude a slug from a cluster: remove it from `merge_slugs`.",
        "",
        "merges:",
    ]
    for c in clusters:
        approved_default = "true" if c["confidence"] == "HIGH" else "false"
        lines.append(f"  - confidence: {c['confidence']}")
        lines.append(f"    approved: {approved_default}")
        lines.append(f"    canonical_name: {json.dumps(c['canonical_name'], ensure_ascii=False)}")
        lines.append(f"    canonical_slug: {c['canonical_slug']}")
        lines.append(f"    reason: {json.dumps(c['reason'])}")
        lines.append(f"    merge_slugs:")
        for m in c["members"]:
            if m["slug"] != c["canonical_slug"]:
                lines.append(f"      - {m['slug']}")
        lines.append(f"    member_names:  # for reference, do not edit")
        for m in c["members"]:
            lines.append(f"      - {json.dumps(m['name'], ensure_ascii=False)}")
        lines.append("")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("facet", choices=["persons", "topics", "key-ideas"])
    args = ap.parse_args()

    facet_dir = WIKI / args.facet
    if not facet_dir.exists():
        print(f"ERROR: {facet_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    entries = []
    for p in sorted(facet_dir.glob("*.md")):
        if p.name in ("INDEX.md",):
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        fm = parse_frontmatter(text)
        name = fm.get("name", p.stem)
        sources = set(parse_sources(text))
        contexts: list[str] = []
        summary = parse_summary_line(text)
        if summary:
            contexts.append(summary)
        entries.append({
            "slug": p.stem,
            "name": name.strip('"').strip("'"),
            "normalized": normalize_name(name),
            "sources": sources,
            "contexts": contexts,
        })

    print(f"loaded {len(entries)} entries from {facet_dir}")

    known = load_known_aliases() if args.facet == "persons" else []
    if known:
        print(f"loaded {len(known)} known aliases from memory/")

    clusters = cluster_entries(entries, known)
    by_conf = defaultdict(int)
    for c in clusters:
        by_conf[c["confidence"]] += 1
    print(f"clusters: HIGH={by_conf['HIGH']}, MED={by_conf['MED']}, LOW={by_conf['LOW']}")

    md_path = WIKI / f"_pending-merges-{args.facet}.md"
    yaml_path = WIKI / f"_pending-merges-{args.facet}.yaml"
    md_path.write_text(render_md(args.facet, clusters), encoding="utf-8")
    yaml_path.write_text(render_yaml(args.facet, clusters), encoding="utf-8")
    print(f"wrote {md_path}")
    print(f"wrote {yaml_path}")


if __name__ == "__main__":
    main()
