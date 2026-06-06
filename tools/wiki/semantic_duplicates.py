#!/usr/bin/env python3
"""tools/wiki/semantic_duplicates.py — find probable duplicates by similarity.

Consumes two artefacts produced by the parallel passes:

  · wiki/<facet>/_embeddings.json    — nomic-embed-text vectors (Studio64)
  · wiki/<facet>/_translations.json  — CA/ES/EN equivalents per slug (DS4)

Produces merge candidates from three signals:

  1. **Semantic near-duplicates** — entries whose embedding cosine
     similarity exceeds a per-facet threshold. Catches paraphrases,
     same-meaning-different-words.

  2. **Cross-language slug collisions** — entries where the translation
     (CA or ES or EN) of one slug matches another slug's name exactly.
     Catches `eco-eficiencia` ↔ `energy-efficiency`.

  3. **Translation-pair near-matches** — two entries whose translation
     fingerprints (concatenated CA+ES+EN) are highly similar. Catches
     synonyms that didn't trigger 1 or 2 alone.

Outputs a markdown report + apply-ready YAML per facet, same shape as
detect_slug_variants.py.

Usage:
  python3 tools/wiki/semantic_duplicates.py            # all facets
  python3 tools/wiki/semantic_duplicates.py topics --threshold 0.85
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
WIKI = REPO / "wiki"
FACETS = ["persons", "topics", "key-ideas"]

# Per-facet thresholds; conservative-by-default to keep noise low.
DEFAULT_THRESHOLDS = {
    "persons": 0.92,
    "topics": 0.90,
    "key-ideas": 0.88,
}


def slugify(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if (na and nb) else 0.0


def load_json(p: Path) -> dict:
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


# ----------------------------------------------------- signal extractors --

def semantic_pairs(embeddings: dict, threshold: float) -> list[tuple[str, str, float]]:
    """All slug pairs with cosine ≥ threshold."""
    entries = embeddings.get("entries", {})
    items = [(slug, rec.get("vec")) for slug, rec in entries.items() if rec.get("vec")]
    out = []
    for i, (slug_a, vec_a) in enumerate(items):
        for slug_b, vec_b in items[i + 1 :]:
            c = cosine(vec_a, vec_b)
            if c >= threshold:
                out.append((slug_a, slug_b, c))
    return sorted(out, key=lambda x: -x[2])


def cross_language_pairs(translations: dict, slug_set: set[str]) -> list[tuple[str, str, str]]:
    """For each entry, check if any of its translations slugifies to a
    DIFFERENT existing slug. Returns (slug_a, slug_b, evidence)."""
    entries = translations.get("entries", {})
    out = []
    for slug, rec in entries.items():
        for lang in ("ca", "es", "en"):
            translated = rec.get(lang, "").strip()
            if not translated:
                continue
            translated_slug = slugify(translated)
            if translated_slug and translated_slug != slug and translated_slug in slug_set:
                out.append((slug, translated_slug, f"{lang}-translation"))
    # De-dup: prefer alphabetical first as slug_a for stable ordering
    seen: set[tuple[str, str]] = set()
    dedup: list[tuple[str, str, str]] = []
    for a, b, evidence in out:
        key = tuple(sorted([a, b]))
        if key in seen:
            continue
        seen.add(key)
        dedup.append((key[0], key[1], evidence))
    return dedup


def translation_overlap_pairs(translations: dict, threshold: int = 2) -> list[tuple[str, str, str]]:
    """Two slugs share ≥`threshold` of their {ca, es, en} translations (case-
    insensitive). Catches conceptual duplicates with different originals."""
    entries = translations.get("entries", {})
    inverted: dict[str, set[str]] = defaultdict(set)
    for slug, rec in entries.items():
        for lang in ("ca", "es", "en"):
            v = rec.get(lang, "").strip().lower()
            if v:
                inverted[v].add(slug)
    pair_hits: dict[tuple[str, str], int] = defaultdict(int)
    for v, slugs in inverted.items():
        if len(slugs) < 2:
            continue
        slugs_list = sorted(slugs)
        for i, a in enumerate(slugs_list):
            for b in slugs_list[i + 1 :]:
                pair_hits[(a, b)] += 1
    return [
        (a, b, f"shares {n} translations")
        for (a, b), n in pair_hits.items()
        if n >= threshold
    ]


# ------------------------------------------------------------- rendering --

def render_section(title: str, pairs: list[tuple[str, str, str]], with_score: bool = False) -> list[str]:
    if not pairs:
        return [f"### {title} (0)\n"]
    out = [f"### {title} ({len(pairs)})\n"]
    if with_score:
        out.append("| Slug A | Slug B | Score |")
        out.append("| --- | --- | --- |")
        for a, b, s in pairs:
            out.append(f"| `{a}` | `{b}` | {s:.3f} |")
    else:
        out.append("| Slug A | Slug B | Evidence |")
        out.append("| --- | --- | --- |")
        for a, b, e in pairs:
            out.append(f"| `{a}` | `{b}` | {e} |")
    out.append("")
    return out


def write_yaml(facet: str, pairs_by_kind: dict, out_path: Path) -> int:
    lines = [
        f"# Pending merges — {facet} (semantic / translation pass)",
        f"# Generated by tools/wiki/semantic_duplicates.py",
        f"# To approve a cluster: set `approved: true`. Then:",
        f"#   python3 tools/wiki/apply_merges.py {facet} \\",
        f"#       --input {out_path.relative_to(REPO)}",
        "",
        "merges:",
    ]
    n = 0
    seen: set[tuple[str, str]] = set()
    for kind, pairs in pairs_by_kind.items():
        for entry in pairs:
            a, b = entry[0], entry[1]
            evidence = entry[2] if len(entry) > 2 else "unknown"
            if isinstance(evidence, float):
                evidence = f"cos={evidence:.3f}"
            key = tuple(sorted([a, b]))
            if key in seen:
                continue
            seen.add(key)
            # Canonical: prefer the LONGER slug (more specific name preserved)
            if len(a) >= len(b):
                canonical, absorbed = a, b
            else:
                canonical, absorbed = b, a
            lines.extend([
                f"  - confidence: MED",
                f"    approved: false",
                f"    canonical_name: \"{canonical}\"",
                f"    canonical_slug: {canonical}",
                f"    reason: \"semantic/translation: {kind} ({evidence})\"",
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
    ap.add_argument("facet", nargs="?", choices=FACETS, default=None)
    ap.add_argument("--threshold", type=float, default=None,
                    help="Cosine threshold override (default: per-facet)")
    ap.add_argument("--out", default="wiki/_pending-semantic-duplicates.md",
                    help="Markdown report path")
    ap.add_argument("--yaml-prefix", default="wiki/_pending-semantic-duplicates",
                    help="Per-facet YAML prefix")
    args = ap.parse_args()
    facets = [args.facet] if args.facet else FACETS

    full = ["# Pending semantic / translation duplicates\n"]
    full.append(
        "Generated by `tools/wiki/semantic_duplicates.py`. Combines two signals:\n\n"
        "1. **Embedding cosine similarity** (Studio64 nomic-embed-text) — "
        "catches paraphrases, same-meaning-different-words.\n"
        "2. **Translation slug-collision** (DS4 CA/ES/EN translations) — "
        "catches cross-language duplicates (e.g. `eco-eficiencia` ↔ "
        "`energy-efficiency`).\n\n"
        "Per-facet YAML in apply_merges.py schema is written alongside. "
        "All clusters land with `approved: false`.\n"
    )
    yaml_totals: dict[str, int] = {}
    for facet in facets:
        facet_dir = WIKI / facet
        embeddings = load_json(facet_dir / "_embeddings.json")
        translations = load_json(facet_dir / "_translations.json")
        slug_set = {p.stem for p in facet_dir.glob("*.md") if p.name != "INDEX.md"}
        threshold = args.threshold or DEFAULT_THRESHOLDS.get(facet, 0.90)
        sem = semantic_pairs(embeddings, threshold) if embeddings else []
        cl = cross_language_pairs(translations, slug_set) if translations else []
        ovl = translation_overlap_pairs(translations) if translations else []

        full.append(f"\n## {facet}\n")
        full.append(f"- embedding entries cached: {len(embeddings.get('entries', {}))}")
        full.append(f"- translation entries cached: {len(translations.get('entries', {}))}")
        full.append(f"- cosine threshold: {threshold}\n")
        full.extend(render_section(
            "Semantic near-duplicates (embedding cosine)", sem, with_score=True
        ))
        full.extend(render_section("Cross-language slug collisions", cl))
        full.extend(render_section("Translation-pair overlaps", ovl))

        # Write YAML
        pairs_by_kind = {
            "semantic-cosine": [(a, b, s) for a, b, s in sem],
            "cross-language": cl,
            "translation-overlap": ovl,
        }
        yaml_path = REPO / f"{args.yaml_prefix}-{facet}.yaml"
        yaml_totals[facet] = write_yaml(facet, pairs_by_kind, yaml_path)

    full.append("\n## YAMLs emitted\n")
    for f, n in yaml_totals.items():
        full.append(f"- `_pending-semantic-duplicates-{f}.yaml` — {n} clusters")
    full.append("")

    out_path = REPO / args.out
    out_path.write_text("\n".join(full), encoding="utf-8")
    print(f"wrote {out_path}")
    for f, n in yaml_totals.items():
        print(f"wrote {args.yaml_prefix}-{f}.yaml ({n} clusters)")


if __name__ == "__main__":
    main()
