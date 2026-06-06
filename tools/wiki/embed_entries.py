#!/usr/bin/env python3
"""tools/wiki/embed_entries.py — embed each wiki entry with nomic-embed-text.

For each entry in wiki/<facet>/, build a fingerprint string (name + summary
+ aliases) and request an embedding from Studio64's Ollama nomic-embed-text.
Store the vector keyed by slug in wiki/<facet>/_embeddings.json.

The embeddings feed `tools/wiki/semantic_duplicates.py` — pairwise cosine
similarity then surfaces probable same-entity duplicates the lexical
detector misses (cross-language, paraphrased, etc.).

Re-runnable. Idempotent: skips entries whose fingerprint hash matches the
cached embedding's source-hash (so re-running after enrichment re-embeds
only the changed entries).

Uses direct HTTP to skip subprocess overhead — embedding ~3000 entries
takes a few minutes versus ~50 min via the CLI.

Usage:
  python3 tools/wiki/embed_entries.py            # all facets
  python3 tools/wiki/embed_entries.py persons    # one facet
  python3 tools/wiki/embed_entries.py --force    # re-embed all
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
WIKI = REPO / "wiki"
STUDIO64 = "http://192.168.1.47:11434"
MODEL = "nomic-embed-text:latest"
FACETS = ["persons", "topics", "key-ideas"]

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm = {}
    aliases = []
    in_aliases = False
    for line in m.group(1).splitlines():
        if line.startswith("aliases:"):
            in_aliases = True
            continue
        if in_aliases and re.match(r"^\s*-\s+", line):
            aliases.append(re.sub(r"^\s*-\s+", "", line).strip().strip('"').strip("'"))
            continue
        in_aliases = False
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"').strip("'")
    fm["aliases"] = aliases
    return fm


def extract_summary(text: str) -> str:
    m = re.search(r"## Summary\s*\n+(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if not m:
        return ""
    s = m.group(1).strip()
    # Drop bullet-list-only summaries — useless for similarity
    if s.startswith("*[") and s.endswith("]*"):
        return ""
    return s


def build_fingerprint(facet: str, slug: str, fm: dict, summary: str) -> str:
    name = fm.get("name", slug)
    aliases = fm.get("aliases", [])
    parts = [name]
    if aliases:
        parts.append(f"(aliases: {', '.join(aliases)})")
    if summary:
        parts.append(summary)
    return " — ".join(parts)


def fingerprint_hash(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def embed(text: str) -> list[float]:
    payload = json.dumps({"model": MODEL, "prompt": text}).encode("utf-8")
    req = urllib.request.Request(
        f"{STUDIO64}/api/embeddings",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
    return data.get("embedding") or []


def load_existing(out_path: Path) -> dict:
    if not out_path.exists():
        return {"model": MODEL, "entries": {}}
    try:
        return json.loads(out_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"model": MODEL, "entries": {}}


def save_atomic(out_path: Path, data: dict):
    tmp = out_path.with_suffix(out_path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    tmp.replace(out_path)


def embed_facet(facet: str, force: bool) -> dict:
    facet_dir = WIKI / facet
    out_path = facet_dir / "_embeddings.json"
    existing = load_existing(out_path)
    if existing.get("model") != MODEL:
        existing = {"model": MODEL, "entries": {}}

    entries = existing["entries"]
    todo = []
    skipped = 0
    for p in sorted(facet_dir.glob("*.md")):
        if p.name == "INDEX.md":
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        fm = parse_frontmatter(text)
        summary = extract_summary(text)
        fp = build_fingerprint(facet, p.stem, fm, summary)
        fp_hash = fingerprint_hash(fp)
        rec = entries.get(p.stem)
        if not force and rec and rec.get("fp_hash") == fp_hash:
            skipped += 1
            continue
        todo.append((p.stem, fp, fp_hash))

    print(f"  {facet}: {len(todo)} to embed ({skipped} cached)")
    if not todo:
        return existing

    t0 = time.time()
    save_every = 50
    for i, (slug, fp, fp_hash) in enumerate(todo, 1):
        try:
            vec = embed(fp)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            print(f"  [{i}/{len(todo)}] ✗ {slug}: {e}", file=sys.stderr)
            continue
        entries[slug] = {"fp_hash": fp_hash, "vec": vec}
        if i % save_every == 0:
            save_atomic(out_path, existing)
            elapsed = time.time() - t0
            rate = i / elapsed
            eta = (len(todo) - i) / rate
            print(f"  {facet}: {i}/{len(todo)} ({rate:.1f}/s, eta {eta/60:.1f}m)")
    save_atomic(out_path, existing)
    elapsed = time.time() - t0
    print(f"  {facet}: done {len(todo)} in {elapsed/60:.1f}m")
    return existing


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("facet", nargs="?", choices=FACETS, default=None)
    ap.add_argument("--force", action="store_true",
                    help="re-embed every entry, even cached ones")
    args = ap.parse_args()

    facets = [args.facet] if args.facet else FACETS
    t0 = time.time()
    for f in facets:
        embed_facet(f, args.force)
    print(f"\ntotal: {(time.time()-t0)/60:.1f}m")


if __name__ == "__main__":
    main()
