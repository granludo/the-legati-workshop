#!/usr/bin/env python3
"""tools/wiki/search.py — semantic search over the wiki.

Takes a natural-language query, embeds it via Studio64's nomic-embed-text,
scores against every cached entry embedding, returns the top-K matches.

Useful when Marc / Agatha is drafting and wants to find related wiki
entries by meaning rather than exact slug or token. Cross-language friendly
(nomic-embed-text is multilingual).

Usage:
  python3 tools/wiki/search.py "AI safety in education"
  python3 tools/wiki/search.py "soberania tecnologica" --facet topics --top 20
  python3 tools/wiki/search.py "Karpathy" --facet persons
  python3 tools/wiki/search.py "function calling vs tool use" --all-facets
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
WIKI = REPO / "wiki"
STUDIO64 = "http://192.168.1.47:11434"
MODEL = "nomic-embed-text:latest"
FACETS = ["persons", "topics", "key-ideas"]


def embed(text: str) -> list[float]:
    payload = json.dumps({"model": MODEL, "prompt": text}).encode("utf-8")
    req = urllib.request.Request(
        f"{STUDIO64}/api/embeddings",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read()).get("embedding") or []


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if (na and nb) else 0.0


def search_facet(facet: str, query_vec: list[float], top: int) -> list[tuple[str, float]]:
    emb_path = WIKI / facet / "_embeddings.json"
    if not emb_path.exists():
        return []
    data = json.loads(emb_path.read_text(encoding="utf-8"))
    entries = data.get("entries", {})
    scored: list[tuple[str, float]] = []
    for slug, rec in entries.items():
        vec = rec.get("vec")
        if not vec:
            continue
        scored.append((slug, cosine(query_vec, vec)))
    scored.sort(key=lambda x: -x[1])
    return scored[:top]


def entry_name(facet: str, slug: str) -> str:
    """Pull the `name:` frontmatter from a wiki entry, or return slug."""
    p = WIKI / facet / f"{slug}.md"
    if not p.exists():
        return slug
    try:
        text = p.read_text(encoding="utf-8")
    except OSError:
        return slug
    for line in text.split("\n"):
        if line.startswith("name:"):
            return line[5:].strip().strip('"').strip("'")
        if line == "---" and "name:" not in text[:200]:
            break
    return slug


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", help="Natural-language query (in any of CA/ES/EN)")
    ap.add_argument("--facet", choices=FACETS, default=None,
                    help="Limit to one facet (default: all)")
    ap.add_argument("--top", type=int, default=10, help="Top-K per facet")
    ap.add_argument("--all-facets", action="store_true",
                    help="Show top-K from every facet")
    args = ap.parse_args()

    try:
        qv = embed(args.query)
    except Exception as e:
        sys.exit(f"embedding endpoint unreachable: {e}")

    if not qv:
        sys.exit("empty embedding — Studio64 returned no vector")

    facets = [args.facet] if args.facet else FACETS

    for facet in facets:
        results = search_facet(facet, qv, args.top)
        if not results:
            print(f"\n{facet}: (no embeddings cached — run tools/wiki/embed_entries.py)")
            continue
        print(f"\n## {facet}")
        for slug, score in results:
            name = entry_name(facet, slug)
            display = f"{name}" if name != slug else slug
            print(f"  {score:.3f}  [[{facet}/{slug}]]  {display}")


if __name__ == "__main__":
    main()
