#!/usr/bin/env python3
"""tools/wiki/merge_proposals.py — consolidate all merge signals into one queue.

We now have FIVE detectors producing per-facet YAML candidate lists:

  1. propose_merges.py            → _pending-merges-<facet>.yaml
  2. detect_slug_variants.py      → _pending-slug-variants-<facet>.yaml
  3. semantic_duplicates.py       → _pending-semantic-duplicates-<facet>.yaml

For Marc-review ergonomics, one ranked queue is friendlier than five.
This script reads all the per-facet YAMLs, groups by the unordered pair
{slug_a, slug_b}, attaches the union of evidence strings, and assigns
a confidence based on detector overlap:

  · 3+ detectors agree → HIGH    (almost certainly the same entity)
  · 2 detectors agree  → MED     (worth Marc's careful read)
  · 1 detector only    → LOW     (judgment call, often false positive)

Writes `wiki/_merge-proposals-<facet>.yaml` (apply_merges schema) +
`wiki/_merge-proposals.md` (single ranked review surface).

Usage:
  python3 tools/wiki/merge_proposals.py            # all facets
  python3 tools/wiki/merge_proposals.py topics     # one facet
"""
from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
WIKI = REPO / "wiki"
FACETS = ["persons", "topics", "key-ideas"]

YAML_SOURCES = {
    "propose": "_pending-merges-{facet}.yaml",
    "slug-variant": "_pending-slug-variants-{facet}.yaml",
    "semantic": "_pending-semantic-duplicates-{facet}.yaml",
}


def parse_clusters(yaml_path: Path) -> list[dict]:
    """Minimal YAML parser for our cluster schema. Each cluster is a dict with
    keys canonical_slug, merge_slugs (list), reason."""
    if not yaml_path.exists():
        return []
    out = []
    current: dict | None = None
    in_merge_slugs = False
    in_member_names = False
    for raw_line in yaml_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if line.startswith("  - confidence:"):
            if current:
                out.append(current)
            current = {"merge_slugs": [], "member_names": []}
            in_merge_slugs = in_member_names = False
            continue
        if current is None:
            continue
        if line.lstrip().startswith("merge_slugs:"):
            in_merge_slugs = True
            in_member_names = False
            continue
        if line.lstrip().startswith("member_names:"):
            in_member_names = True
            in_merge_slugs = False
            continue
        if (in_merge_slugs or in_member_names) and re.match(r"^\s+-\s+", line):
            val = re.sub(r"^\s+-\s+", "", line).strip().strip('"').strip("'")
            if in_merge_slugs:
                current["merge_slugs"].append(val)
            else:
                current["member_names"].append(val)
            continue
        in_merge_slugs = in_member_names = False
        m = re.match(r"^\s+(\w+):\s*(.*)$", line)
        if m:
            current[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    if current:
        out.append(current)
    return out


def normalize_pair(canonical: str, absorbed: str) -> tuple[str, str]:
    """Return a stable pair key (alphabetical) so we group regardless of which
    detector picked which side as canonical."""
    return (canonical, absorbed) if canonical <= absorbed else (absorbed, canonical)


def aggregate(facet: str) -> dict[tuple[str, str], dict]:
    """For each pair across all source YAMLs: return aggregated metadata."""
    out: dict[tuple[str, str], dict] = {}
    for detector, template in YAML_SOURCES.items():
        path = WIKI / template.format(facet=facet)
        clusters = parse_clusters(path)
        for c in clusters:
            canonical = c.get("canonical_slug", "")
            absorbs = c.get("merge_slugs", [])
            reason = c.get("reason", "")
            for ab in absorbs:
                key = normalize_pair(canonical, ab)
                if key not in out:
                    out[key] = {
                        "detectors": set(),
                        "reasons": [],
                        # Track which detector picked which side as canonical
                        "canonical_votes": defaultdict(int),
                    }
                out[key]["detectors"].add(detector)
                out[key]["reasons"].append(f"{detector}: {reason}")
                out[key]["canonical_votes"][canonical] += 1
    return out


def pick_canonical(pair: tuple[str, str], votes: dict) -> tuple[str, str]:
    """Tie-break: most votes; tie → longer slug (preserves more name detail)."""
    if not votes:
        return pair
    sorted_votes = sorted(votes.items(), key=lambda kv: (-kv[1], -len(kv[0])))
    canonical = sorted_votes[0][0]
    absorbed = pair[0] if pair[0] != canonical else pair[1]
    return canonical, absorbed


def confidence(n_detectors: int) -> str:
    if n_detectors >= 3:
        return "HIGH"
    if n_detectors == 2:
        return "MED"
    return "LOW"


def write_yaml(facet: str, aggregated: dict, out_path: Path) -> int:
    lines = [
        f"# Pending merges — {facet} (unified review queue)",
        f"# Generated by tools/wiki/merge_proposals.py",
        f"# Confidence: HIGH = 3+ detectors agree, MED = 2 detectors, LOW = 1 only.",
        f"# To approve: set `approved: true`. Then:",
        f"#   python3 tools/wiki/apply_merges.py {facet} --input {out_path.relative_to(REPO)}",
        "",
        "merges:",
    ]
    n_high = n_med = n_low = 0
    # Sort by confidence then alphabetical
    sorted_pairs = sorted(
        aggregated.items(),
        key=lambda kv: (-len(kv[1]["detectors"]), kv[0][0])
    )
    for (slug_a, slug_b), data in sorted_pairs:
        n_det = len(data["detectors"])
        conf = confidence(n_det)
        if conf == "HIGH":
            n_high += 1
        elif conf == "MED":
            n_med += 1
        else:
            n_low += 1
        canonical, absorbed = pick_canonical((slug_a, slug_b), data["canonical_votes"])
        detector_list = ", ".join(sorted(data["detectors"]))
        lines.extend([
            f"  - confidence: {conf}",
            f"    approved: false",
            f"    canonical_name: \"{canonical}\"",
            f"    canonical_slug: {canonical}",
            f"    reason: \"detectors: {detector_list} ({n_det})\"",
            f"    merge_slugs:",
            f"      - {absorbed}",
            f"    member_names:  # for reference, do not edit",
            f"      - \"{canonical}\"",
            f"      - \"{absorbed}\"",
            "",
        ])
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return n_high, n_med, n_low


def render_md_summary(facet: str, aggregated: dict, n_h: int, n_m: int, n_l: int) -> list[str]:
    lines = [f"\n## {facet}\n"]
    lines.append(f"- HIGH (3+ detectors): **{n_h}**")
    lines.append(f"- MED (2 detectors): **{n_m}**")
    lines.append(f"- LOW (1 detector):  **{n_l}**")
    lines.append(f"- total candidate pairs: {n_h + n_m + n_l}\n")

    # HIGH section — these are very likely true duplicates
    if n_h:
        lines.append("### HIGH-confidence pairs (3+ detectors agree)\n")
        lines.append("| Slug A | Slug B | Detectors |")
        lines.append("| --- | --- | --- |")
        for (a, b), data in sorted(
            aggregated.items(),
            key=lambda kv: (-len(kv[1]["detectors"]), kv[0][0]),
        ):
            if len(data["detectors"]) < 3:
                continue
            lines.append(f"| `{a}` | `{b}` | {', '.join(sorted(data['detectors']))} |")
        lines.append("")

    # MED — preview a sample
    if n_m:
        lines.append("### MED-confidence sample (first 30)\n")
        lines.append("| Slug A | Slug B | Detectors |")
        lines.append("| --- | --- | --- |")
        shown = 0
        for (a, b), data in sorted(
            aggregated.items(),
            key=lambda kv: (-len(kv[1]["detectors"]), kv[0][0]),
        ):
            if len(data["detectors"]) != 2:
                continue
            lines.append(f"| `{a}` | `{b}` | {', '.join(sorted(data['detectors']))} |")
            shown += 1
            if shown >= 30:
                break
        lines.append("")

    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("facet", nargs="?", choices=FACETS, default=None)
    args = ap.parse_args()
    facets = [args.facet] if args.facet else FACETS

    summary = ["# Unified merge-proposal review queue\n"]
    summary.append(
        "Generated by `tools/wiki/merge_proposals.py`. Consolidates "
        "candidates from propose_merges.py, detect_slug_variants.py, and "
        "semantic_duplicates.py into one ranked queue per facet.\n\n"
        "**Confidence rule:** 3+ independent detectors agree → HIGH; 2 → "
        "MED; 1 only → LOW. HIGH pairs are very likely true duplicates; "
        "MED warrants careful review; LOW is mostly judgment-call territory.\n"
    )

    for facet in facets:
        aggregated = aggregate(facet)
        out_yaml = WIKI / f"_merge-proposals-{facet}.yaml"
        n_h, n_m, n_l = write_yaml(facet, aggregated, out_yaml)
        print(f"{facet}: HIGH={n_h} MED={n_m} LOW={n_l} → {out_yaml.name}")
        summary.extend(render_md_summary(facet, aggregated, n_h, n_m, n_l))

    summary_path = WIKI / "_merge-proposals.md"
    summary_path.write_text("\n".join(summary), encoding="utf-8")
    print(f"wrote {summary_path}")


if __name__ == "__main__":
    main()
