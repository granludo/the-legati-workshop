#!/usr/bin/env python3
"""tools/wiki/detect_slug_variants.py — find probable same-entity duplicates.

The propose_merges.py heuristic is conservative: it caught plural/singular,
acronym/expansion, and accent variants in the first round, but it MISSES
several patterns that show up in practice:

  (a) initial-vs-full-name:   `n-galanis` ↔ `nikolaos-galanis`
  (b) compound vs short:      `francisco-garcia` ↔ `francisco-garcia-penalvo`
  (c) "et al" leak:           `e-sanagar-darbani` ↔ `sanagar-darbani-et-al`
  (d) doubled slug:           `miguel-angel-conde-miguel-angel-conde-gonzalez`
  (e) spelling variant:       `nikolaos-galanis` ↔ `nikolas-galanis`

This scanner walks each facet and surfaces pairs matching these patterns,
ordered by confidence. Output is a markdown report — input for the next
round of Marc-reviewed merges.

Usage:
  python3 tools/wiki/detect_slug_variants.py persons     # one facet
  python3 tools/wiki/detect_slug_variants.py             # all facets
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
WIKI = REPO / "wiki"
FACETS = ["persons", "topics", "key-ideas"]


def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i]
        for j, cb in enumerate(b, 1):
            ins = curr[-1] + 1
            dele = prev[j] + 1
            sub = prev[j - 1] + (0 if ca == cb else 1)
            curr.append(min(ins, dele, sub))
        prev = curr
    return prev[-1]


def detect_initial_vs_full(slugs: list[str]) -> list[tuple[str, str, str]]:
    """Find pairs where one slug starts with a single-letter token that
    plausibly abbreviates the first token of another with matching tail.
    Returns [(short_slug, long_slug, evidence)]."""
    out = []
    by_tail = {}
    for s in slugs:
        parts = s.split("-")
        if len(parts) < 2:
            continue
        tail = tuple(parts[1:])  # everything after first token
        by_tail.setdefault(tail, []).append(s)
    for tail, candidates in by_tail.items():
        if len(candidates) < 2:
            continue
        # Find single-letter-first-token vs full-first-token
        shorts = [c for c in candidates if len(c.split("-")[0]) == 1]
        longs = [c for c in candidates if len(c.split("-")[0]) > 1]
        for short in shorts:
            short_initial = short[0]
            for long_ in longs:
                if long_.split("-")[0].startswith(short_initial):
                    out.append((short, long_, "initial-vs-full-firstname"))
    return out


def detect_compound_subset(slugs: list[str]) -> list[tuple[str, str, str]]:
    """Find pairs where one slug is a prefix of another (compound surname
    truncation). e.g. `francisco-garcia` ⊂ `francisco-garcia-penalvo`.
    Only surfaces if the shorter is ≥2 tokens (to avoid trivial first-name
    collisions)."""
    out = []
    s_set = set(slugs)
    for s in slugs:
        parts = s.split("-")
        if len(parts) < 2:
            continue
        for n in range(len(parts) + 1, min(len(parts) + 4, 6)):
            # check longer slugs that start with this slug + an extra token
            for other in slugs:
                if other == s:
                    continue
                if other.startswith(s + "-"):
                    extra = other[len(s) + 1:]
                    if "-" not in extra and len(extra) >= 2:
                        out.append((s, other, "compound-surname-truncation"))
    # dedupe
    return list({(a, b, r) for a, b, r in out})


def detect_et_al_leak(slugs: list[str]) -> list[tuple[str, str, str]]:
    """`X` ↔ `X-et-al` style."""
    out = []
    s_set = set(slugs)
    for s in slugs:
        if s.endswith("-et-al"):
            base = s[: -len("-et-al")]
            if base in s_set:
                out.append((base, s, "et-al-leak"))
            # also "X-Y et al" where the base has the X-Y prefix but slightly different
            for other in slugs:
                if other == s:
                    continue
                if other.endswith("-" + base.split("-")[-1]) and other != base:
                    out.append((other, s, "et-al-leak-fuzzy"))
    return list({(a, b, r) for a, b, r in out})


def detect_doubled_slug(slugs: list[str]) -> list[tuple[str, str, str]]:
    """Slugs containing themselves twice — `miguel-angel-conde-miguel-angel-conde-gonzalez`."""
    out = []
    for s in slugs:
        # Look for any sub-slug repeated
        parts = s.split("-")
        for n in range(2, min(5, len(parts))):
            head = "-".join(parts[:n])
            rest = "-".join(parts[n:])
            if rest.startswith(head + "-") or rest == head:
                # Find a canonical: the entry without the doubling
                if head in slugs:
                    out.append((head, s, "self-doubled-slug"))
                else:
                    # No clean base; just flag for manual cleanup
                    out.append(("(no clean base)", s, "self-doubled-slug-orphan"))
                break
    return list({(a, b, r) for a, b, r in out})


def detect_spelling_variants(slugs: list[str], threshold: int = 1) -> list[tuple[str, str, str]]:
    """Pairs within Levenshtein distance `threshold` on the LAST-token only.
    e.g. `nikolaos-galanis` ↔ `nikolas-galanis` (last token "galanis" same;
    first token "nikolaos"/"nikolas" differ by 1). Restricted to slugs whose
    last token matches exactly — same surname, different transliteration."""
    out = []
    by_last = {}
    for s in slugs:
        parts = s.split("-")
        if len(parts) < 2 or len(parts[0]) <= 1:
            continue
        last = parts[-1]
        by_last.setdefault(last, []).append(s)
    for last, group in by_last.items():
        if len(group) < 2:
            continue
        for i, a in enumerate(group):
            for b in group[i + 1 :]:
                # Compare first tokens
                fa = a.split("-")[0]
                fb = b.split("-")[0]
                if fa == fb:
                    continue
                d = levenshtein(fa, fb)
                if 0 < d <= threshold:
                    out.append((a, b, f"first-token-edit-distance-{d}"))
    return out


def render_report(facet: str, results: dict[str, list]) -> str:
    lines = [f"## {facet}\n"]
    total = sum(len(v) for v in results.values())
    lines.append(f"**Total candidate pairs: {total}**\n")
    for category, pairs in results.items():
        if not pairs:
            continue
        lines.append(f"### {category} ({len(pairs)})\n")
        lines.append("| Slug A | Slug B | Evidence |")
        lines.append("| --- | --- | --- |")
        for a, b, evidence in sorted(set(pairs)):
            lines.append(f"| `{a}` | `{b}` | {evidence} |")
        lines.append("")
    return "\n".join(lines)


def scan_facet(facet: str) -> dict[str, list]:
    facet_dir = WIKI / facet
    slugs = sorted({p.stem for p in facet_dir.glob("*.md") if p.name != "INDEX.md"})
    out = {
        "initial-vs-full-name": detect_initial_vs_full(slugs),
        "et-al-leak": detect_et_al_leak(slugs),
        "doubled-slug": detect_doubled_slug(slugs),
        "spelling-variants": detect_spelling_variants(slugs),
    }
    # compound-truncation is real signal for persons (Spanish double surnames)
    # but mostly noise for topics/key-ideas (parent ↔ narrowing child pairs that
    # should stay separate — same pattern we rejected in the MED merge round).
    if facet == "persons":
        out["compound-surname-truncation"] = detect_compound_subset(slugs)
    return out


def pair_to_canonical(slug_a: str, slug_b: str, evidence: str) -> tuple[str, str]:
    """Decide which of (a, b) should be canonical and which gets absorbed.

    Heuristics:
      - 'et-al-leak': the non-et-al slug is canonical
      - 'self-doubled-slug': the un-doubled slug is canonical
      - 'initial-vs-full-firstname': the full-name slug is canonical
      - 'compound-surname-truncation': the longer (more complete) slug is canonical
      - 'first-token-edit-distance-*': longer or more-conventional first token wins
                                       (rough tiebreaker — Marc should audit)
    Returns (canonical, absorbed)."""
    if "et-al" in slug_b and "et-al" not in slug_a:
        return slug_a, slug_b
    if "et-al" in slug_a and "et-al" not in slug_b:
        return slug_b, slug_a
    if "doubled" in evidence:
        # the doubled slug is the absorbed one
        if "(no clean base)" in slug_a:
            return slug_b, slug_a
        return slug_a, slug_b
    if "initial-vs-full" in evidence:
        # Single-letter first token → absorbed
        a_first = slug_a.split("-")[0]
        b_first = slug_b.split("-")[0]
        if len(a_first) == 1:
            return slug_b, slug_a
        return slug_a, slug_b
    if "compound-surname-truncation" in evidence:
        # The longer (more complete name) is canonical
        if len(slug_a) >= len(slug_b):
            return slug_a, slug_b
        return slug_b, slug_a
    # Spelling-variant tiebreaker: longer or alphabetically-second
    if len(slug_a) > len(slug_b):
        return slug_a, slug_b
    if len(slug_b) > len(slug_a):
        return slug_b, slug_a
    return (slug_a, slug_b) if slug_a < slug_b else (slug_b, slug_a)


def write_yaml(facet: str, results: dict[str, list], out_path: Path) -> int:
    """Emit a YAML in the apply_merges.py schema for the proposed pairs.
    All entries written with `approved: false` so Marc reviews before apply.
    Returns number of clusters written."""
    lines = [
        f"# Pending merges — {facet} (slug-variant pass)",
        f"# Generated by tools/wiki/detect_slug_variants.py",
        f"# To approve a cluster: set `approved: true`. Then:",
        f"#   python3 tools/wiki/apply_merges.py {facet} \\",
        f"#       --input {out_path.relative_to(REPO)}",
        "",
        "merges:",
    ]
    n = 0
    seen_pairs: set[tuple[str, str]] = set()
    for category, pairs in results.items():
        for slug_a, slug_b, evidence in sorted(set(pairs)):
            if "no clean base" in slug_a:
                continue  # cannot auto-resolve; surfaced in MD only
            canonical, absorbed = pair_to_canonical(slug_a, slug_b, evidence)
            key = tuple(sorted([canonical, absorbed]))
            if key in seen_pairs:
                continue
            seen_pairs.add(key)
            lines.extend([
                f"  - confidence: MED",
                f"    approved: false",
                f"    canonical_name: \"{canonical}\"",
                f"    canonical_slug: {canonical}",
                f"    reason: \"slug-variant: {category} ({evidence})\"",
                f"    merge_slugs:",
                f"      - {absorbed}",
                f"    member_names:  # for reference, do not edit",
                f"      - \"{canonical}\"",
                f"      - \"{absorbed}\"",
                "",
            ])
            n += 1
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("facet", nargs="?", choices=FACETS, default=None,
                    help="One facet only (default: all facets)")
    ap.add_argument("--out", default="wiki/_pending-slug-variants.md",
                    help="Output markdown report path")
    ap.add_argument("--yaml-prefix", default="wiki/_pending-slug-variants",
                    help="Per-facet YAML output prefix; emits <prefix>-<facet>.yaml")
    args = ap.parse_args()
    facets = [args.facet] if args.facet else FACETS

    full = ["# Pending slug-variant merges\n"]
    full.append(
        "Generated by `tools/wiki/detect_slug_variants.py`. Surfaces probable "
        "same-entity duplicates the propose_merges.py heuristic misses (initial-"
        "vs-full names, compound surname truncations, et-al leaks, doubled "
        "slugs, transliteration variants). Marc to review and feed into the next "
        "merge round.\n\n"
        "A per-facet YAML in `apply_merges.py` schema is also generated at "
        "`_pending-slug-variants-<facet>.yaml` — toggle `approved: true` and "
        "run `python3 tools/wiki/apply_merges.py <facet> --yaml <path>`.\n"
    )
    grand = 0
    yaml_totals = {}
    for facet in facets:
        results = scan_facet(facet)
        grand += sum(len(v) for v in results.values())
        full.append(render_report(facet, results))
        yaml_path = REPO / f"{args.yaml_prefix}-{facet}.yaml"
        yaml_totals[facet] = write_yaml(facet, results, yaml_path)
    full.append(f"---\n\n**Grand total candidate pairs across all facets: {grand}**\n")
    full.append(
        "\n## YAMLs emitted\n\n"
        + "\n".join(
            f"- `_pending-slug-variants-{f}.yaml` — {n} clusters" for f, n in yaml_totals.items()
        )
        + "\n"
    )

    out_path = REPO / args.out
    out_path.write_text("\n".join(full), encoding="utf-8")
    print(f"wrote {out_path}")
    for facet, n in yaml_totals.items():
        print(f"wrote {args.yaml_prefix}-{facet}.yaml ({n} clusters)")
    print(f"grand total candidates: {grand}")


if __name__ == "__main__":
    main()
