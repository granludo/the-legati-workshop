#!/usr/bin/env python3
"""tools/wiki/translate_aliases.py — generate CA/ES/EN equivalents for each slug.

For every wiki entry, asks DS4 to render the canonical name in Catalan,
Spanish, and English. Saves to wiki/<facet>/_translations.json keyed by slug.

Downstream: `tools/wiki/semantic_duplicates.py` cross-references the
translations against existing slugs in the same facet, surfacing
cross-language duplicates (e.g. `eco-eficiencia` ↔ `energy-efficiency`)
the lexical detector misses.

Re-runnable. Idempotent: skips entries already in the cache. Use --force
to re-translate.

Routes through DS4 (tom-nook.35) per Tier-1a rule. Each call ~8-12s.
Topics (~1,386): ~3h. Key-ideas (~1,089): ~2.5h. Persons: skipped
(person names are language-invariant by default).

Usage:
  python3 tools/wiki/translate_aliases.py            # topics + key-ideas
  python3 tools/wiki/translate_aliases.py topics     # one facet
  python3 tools/wiki/translate_aliases.py --force    # re-translate all
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
WIKI = REPO / "wiki"
DS4_HELPER = REPO / "tools" / "ds4" / "call.py"
DS4_MODEL = "deepseek-v4-flash"
FACETS = ["topics", "key-ideas"]

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)

SYSTEM_PROMPT = """You translate short wiki topic / key-idea names between Catalan (CA), Spanish (ES), and English (EN). The input is one phrase. Render the equivalents in the other two languages plus echo back the input language. Preserve technical idiom and academic register.

Output ONLY a single JSON object — no markdown fences, no commentary:

{"ca": "<catalan>", "es": "<spanish>", "en": "<english>", "input_lang": "<ca|es|en>"}

Rules:
- If a term has no natural translation (proper nouns, acronyms like "MCP", made-up neologisms), repeat the input verbatim for that field.
- Use the academic/technical register, not colloquial.
- Single phrase, no quotation marks inside values.
"""


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm


def call_ds4(system: str, user: str) -> str:
    proc = subprocess.run(
        ["python3", str(DS4_HELPER), "generate",
         "--model", DS4_MODEL,
         "--system", system],
        input=user,
        text=True,
        capture_output=True,
        timeout=120,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ds4 returned {proc.returncode}: {proc.stderr[:200]}")
    return proc.stdout


def parse_json_lenient(s: str) -> dict:
    s = s.strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?\s*", "", s)
        s = re.sub(r"\s*```\s*$", "", s)
    start, end = s.find("{"), s.rfind("}")
    if start < 0 or end <= start:
        raise ValueError(f"no JSON object in: {s[:200]}")
    return json.loads(s[start : end + 1])


def load_existing(out_path: Path) -> dict:
    if not out_path.exists():
        return {"model": DS4_MODEL, "entries": {}}
    try:
        return json.loads(out_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"model": DS4_MODEL, "entries": {}}


def save_atomic(out_path: Path, data: dict):
    tmp = out_path.with_suffix(out_path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(out_path)


def translate_facet(facet: str, force: bool) -> None:
    facet_dir = WIKI / facet
    out_path = facet_dir / "_translations.json"
    existing = load_existing(out_path)
    entries = existing["entries"]

    candidates = []
    for p in sorted(facet_dir.glob("*.md")):
        if p.name == "INDEX.md":
            continue
        slug = p.stem
        if not force and slug in entries:
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        fm = parse_frontmatter(text)
        name = fm.get("name", slug)
        candidates.append((slug, name))

    print(f"  {facet}: {len(candidates)} to translate (already cached: {len(entries)})", flush=True)
    if not candidates:
        return

    t0 = time.time()
    save_every = 25
    failures = 0
    for i, (slug, name) in enumerate(candidates, 1):
        t1 = time.time()
        try:
            raw = call_ds4(SYSTEM_PROMPT, name)
            data = parse_json_lenient(raw)
        except (RuntimeError, ValueError, subprocess.TimeoutExpired, json.JSONDecodeError) as e:
            failures += 1
            print(f"  [{i}/{len(candidates)}] ✗ {slug}: {type(e).__name__}", flush=True)
            continue
        entries[slug] = {
            "name": name,
            "ca": data.get("ca", "").strip(),
            "es": data.get("es", "").strip(),
            "en": data.get("en", "").strip(),
            "input_lang": data.get("input_lang", "").strip(),
        }
        dt = time.time() - t1
        if i % save_every == 0:
            save_atomic(out_path, existing)
            elapsed = time.time() - t0
            rate = i / elapsed
            eta = (len(candidates) - i) / rate / 60
            print(f"  {facet}: {i}/{len(candidates)} ({rate:.2f}/s, eta {eta:.1f}m, fail {failures})", flush=True)
    save_atomic(out_path, existing)
    elapsed = time.time() - t0
    print(f"  {facet}: done {len(candidates)} in {elapsed/60:.1f}m, failures: {failures}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("facet", nargs="?", choices=FACETS, default=None)
    ap.add_argument("--force", action="store_true",
                    help="re-translate every entry, even cached ones")
    args = ap.parse_args()

    facets = [args.facet] if args.facet else FACETS
    t0 = time.time()
    for f in facets:
        translate_facet(f, args.force)
    print(f"\ntotal: {(time.time()-t0)/60:.1f}m")


if __name__ == "__main__":
    main()
