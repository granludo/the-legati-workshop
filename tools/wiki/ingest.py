#!/usr/bin/env python3
"""tools/wiki/ingest.py — single-source ingest into the wiki.

Walks a freshly-landed source through the same extraction the bootstrap
pipeline uses (persons / topics / key_ideas / external_references), then
proposes wiki updates:

  · existing entry → append a timeline entry pointing at the new source
  · new entity     → scaffold a wiki/<facet>/<slug>.md file

Conservative by design. Default is --dry-run: prints the proposed change
set and stops. Pass --apply to actually write entries.

Routes the extraction call through DS4 (DeepSeek V4 Flash on
tom-nook.35:8000) per the Tier-1a routing rule in CLAUDE.md — bulk
mechanical extraction is what DS4 was put in place for.

Idempotent: re-ingesting the same source detects an existing timeline
reference and does not double-add.

Usage:
  python3 tools/wiki/ingest.py <source-path>            # dry-run, show diff
  python3 tools/wiki/ingest.py --apply <source-path>    # apply changes
  python3 tools/wiki/ingest.py --apply --top 12 <path>  # also limit per-facet
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
WIKI = REPO / "wiki"
CACHE = REPO / "tools" / "wiki" / "cache"
DS4_HELPER = REPO / "tools" / "ds4" / "call.py"
DS4_MODEL = "deepseek-v4-flash"
OLLAMA_HELPER = REPO / "tools" / "ollama" / "call.py"
OLLAMA_MODEL = "qwen3.5:122b"  # big-guns rule; tools/ollama/call.py probes studio64 (.47) only
# Backend switch. Default DS4 (DeepSeek V4 Flash on tom-nook). Set
# WIKI_INGEST_LLM=ollama to route through qwen3.5:122b on studio64 instead —
# used when tom-nook must stay free for other work.
LLM_BACKEND = os.environ.get("WIKI_INGEST_LLM", "ds4").lower()

PROMPT_TEMPLATE = """You are analyzing a markdown file from Marc Alier's writing workshop.

Marc Alier is a UPC professor (Barcelona) who writes about AI in education, software engineering, free software, and personalized learning. He works in Catalan, Spanish, and English.

Read the file content below. Output ONLY a single JSON object — no markdown fences, no explanation.

Required JSON shape:

{{
  "summary": "2-3 sentences, matter-of-fact, plain. No marketing voice. No flourish.",
  "persons_mentioned": [{{"name": "Full Name", "context": "one short line on why they're here"}}],
  "topics": ["short tag", "short tag"],
  "key_ideas": ["concept-name"],
  "external_references": ["title or URL"]
}}

Rules:
- persons_mentioned: humans only, named individuals. Skip Marc Alier (the author). Skip Mycroft, Agatha, Bilby (they are AI legati indexed separately). Preserve Catalan/Spanish names with diacritics. Use full names when given; surname-only OK if that's all the file uses.
- topics: 1-5 short tag-style strings, kebab-case-ish ("ai-in-education", "moodle-architecture", "free-software"). Skip overly generic tags ("technology", "writing").
- key_ideas: 0-3 named intellectual positions or concepts ("ai-is-a-tool-not-a-palantir", "baptists-and-bootleggers", "soberania-tecnologica"). Only include if the FILE actually develops or uses the idea — not if it just brushes past.
- external_references: 0-10 paper titles, book titles, films, named URLs. Skip internal repo references.
- If the file is empty, trivial, or purely metadata, still return valid JSON with empty arrays.

FILE PATH: {path}

FILE CONTENT:
---
{content}
---

JSON output:
"""

ENTRY_SCAFFOLD = """---
type: {facet_singular}
slug: {slug}
name: {name}
status: active
first-seen: {today}
last-touched: {today}
sources-count: 1
---
## Summary

*[scaffold — added by ingest.py from a single source; fill on next pass]*

## Timeline

- {today} — [[{source_path}]] · ingested via /add-source

## Evolution

*[open threads / next moves to fill]*

## Sources

- [[{source_path}]]

## Co-occurrence

*[rebuild via tools/wiki/build_cooccurrence.py after ingest]*
"""

FACET_SINGULAR = {
    "persons": "person",
    "topics": "topic",
    "key-ideas": "key-idea",
}


def slugify(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def file_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def cache_get(key: str):
    f = CACHE / f"{key}.json"
    if f.exists():
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
    return None


def cache_put(key: str, data):
    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE / f"{key}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def call_llm(prompt: str) -> str:
    """Single extraction call. Backend chosen by WIKI_INGEST_LLM.

    'ds4' (default): DeepSeek V4 Flash on tom-nook via tools/ds4/call.py.
    'ollama'       : qwen3.5:122b on studio64 via tools/ollama/call.py, with
                     --num-ctx 16384 to respect the 16k-context rule. Used
                     when tom-nook must stay free.
    """
    if LLM_BACKEND == "ollama":
        tmp = None
        try:
            with tempfile.NamedTemporaryFile(
                "w", suffix=".txt", delete=False, encoding="utf-8"
            ) as tf:
                tf.write(prompt)
                tmp = tf.name
            res = subprocess.run(
                ["python3", str(OLLAMA_HELPER), "generate",
                 "--model", OLLAMA_MODEL, "--num-ctx", "16384",
                 "--no-stream", "--in", tmp],
                text=True,
                capture_output=True,
                check=False,
            )
        finally:
            if tmp and os.path.exists(tmp):
                os.unlink(tmp)
        if res.returncode != 0:
            sys.stderr.write(f"[ollama] non-zero exit ({res.returncode}):\n{res.stderr}\n")
        return res.stdout
    res = subprocess.run(
        ["python3", str(DS4_HELPER), "generate", "--model", DS4_MODEL],
        input=prompt,
        text=True,
        capture_output=True,
        check=False,
    )
    if res.returncode != 0:
        sys.stderr.write(f"[ds4] non-zero exit ({res.returncode}):\n{res.stderr}\n")
    return res.stdout


def parse_json_lenient(s: str) -> dict:
    """Best-effort JSON extraction from model output."""
    s = s.strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?\s*", "", s)
        s = re.sub(r"\s*```\s*$", "", s)
    # Find the outermost { ... }
    start = s.find("{")
    end = s.rfind("}")
    if start < 0 or end <= start:
        raise ValueError(f"no JSON object found in:\n{s[:300]}")
    return json.loads(s[start : end + 1])


def extract(source_path: Path) -> dict:
    content = source_path.read_text(encoding="utf-8", errors="ignore")
    key = file_hash(content)
    cached = cache_get(key)
    if cached:
        return cached
    rel = str(source_path.relative_to(REPO))
    prompt = PROMPT_TEMPLATE.format(path=rel, content=content)
    raw = call_llm(prompt)
    data = parse_json_lenient(raw)
    cache_put(key, data)
    return data


# ----------------------------------------------------- wiki entry mutation --

TIMELINE_RE = re.compile(r"^## Timeline\b.*?(?=^## |\Z)", re.MULTILINE | re.DOTALL)
SOURCES_RE = re.compile(r"^## Sources\b.*?(?=^## |\Z)", re.MULTILINE | re.DOTALL)


def now_date() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def has_source_ref(entry_text: str, source_rel: str) -> bool:
    """Idempotency check: source already referenced in the entry?"""
    return f"[[{source_rel}]]" in entry_text


def append_timeline(entry_text: str, source_rel: str, date: str) -> str:
    """Insert a new timeline bullet at the END of the Timeline section."""
    new_line = f"- {date} — [[{source_rel}]] · ingested via /add-source"
    m = TIMELINE_RE.search(entry_text)
    if not m:
        # No Timeline section — synthesize one before Evolution / Sources / end
        addition = f"\n## Timeline\n\n{new_line}\n"
        return entry_text.rstrip() + addition + "\n"
    block = m.group(0).rstrip()
    block += f"\n{new_line}\n"
    return entry_text[: m.start()] + block + "\n" + entry_text[m.end() :]


def append_sources(entry_text: str, source_rel: str) -> str:
    """Add a bullet to the Sources section if not already there."""
    bullet = f"- [[{source_rel}]]"
    m = SOURCES_RE.search(entry_text)
    if not m:
        return entry_text.rstrip() + f"\n\n## Sources\n\n{bullet}\n"
    if bullet in m.group(0):
        return entry_text  # already present
    block = m.group(0).rstrip() + f"\n{bullet}\n"
    return entry_text[: m.start()] + block + "\n" + entry_text[m.end() :]


def update_existing(entry_path: Path, source_rel: str, date: str) -> str | None:
    """Returns the new content if changed, None if no change needed."""
    text = entry_path.read_text(encoding="utf-8")
    if has_source_ref(text, source_rel):
        return None  # idempotent: already ingested
    text = append_timeline(text, source_rel, date)
    text = append_sources(text, source_rel)
    return text


def scaffold_new(facet: str, slug: str, name: str, source_rel: str, date: str) -> str:
    return ENTRY_SCAFFOLD.format(
        facet_singular=FACET_SINGULAR.get(facet, "entry"),
        slug=slug,
        name=name,
        today=date,
        source_path=source_rel,
    )


# --------------------------------------------------------------- ingest run --

def plan_ingest(extracted: dict, source_rel: str, top: int) -> dict:
    date = now_date()
    plan: dict = {"existing_updates": [], "new_entries": [], "skipped_existing": []}

    def per_facet(facet: str, names: list):
        for item in names[:top]:
            if isinstance(item, dict):
                name = item.get("name", "").strip()
            else:
                name = str(item).strip()
            if not name:
                continue
            slug = slugify(name)
            entry_path = WIKI / facet / f"{slug}.md"
            if entry_path.exists():
                new_text = update_existing(entry_path, source_rel, date)
                if new_text is None:
                    plan["skipped_existing"].append((facet, slug, "already references this source"))
                else:
                    plan["existing_updates"].append((facet, slug, entry_path, new_text))
            else:
                content = scaffold_new(facet, slug, name, source_rel, date)
                plan["new_entries"].append((facet, slug, entry_path, content))

    per_facet("persons", extracted.get("persons_mentioned", []))
    per_facet("topics", extracted.get("topics", []))
    per_facet("key-ideas", extracted.get("key_ideas", []))
    return plan


def render_dry_run(plan: dict, extracted: dict):
    print()
    print(f"  summary: {extracted.get('summary', '(none)')[:200]}")
    print()
    print(f"  extraction: {len(extracted.get('persons_mentioned', []))} persons · "
          f"{len(extracted.get('topics', []))} topics · "
          f"{len(extracted.get('key_ideas', []))} key-ideas · "
          f"{len(extracted.get('external_references', []))} ext-refs")
    print()
    print(f"  Existing entries to update ({len(plan['existing_updates'])}):")
    for facet, slug, _path, _new in plan["existing_updates"]:
        print(f"    {facet:10} → {slug}")
    if not plan["existing_updates"]:
        print("    (none)")
    print()
    print(f"  New entries to scaffold ({len(plan['new_entries'])}):")
    for facet, slug, _path, _content in plan["new_entries"]:
        print(f"    {facet:10} + {slug}")
    if not plan["new_entries"]:
        print("    (none)")
    if plan["skipped_existing"]:
        print()
        print(f"  Skipped — idempotent ({len(plan['skipped_existing'])}):")
        for facet, slug, reason in plan["skipped_existing"]:
            print(f"    {facet:10} = {slug}  ({reason})")


def apply_plan(plan: dict):
    n_updated = 0
    n_created = 0
    for _facet, _slug, path, new_text in plan["existing_updates"]:
        path.write_text(new_text, encoding="utf-8")
        n_updated += 1
    for _facet, _slug, path, content in plan["new_entries"]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        n_created += 1
    print(f"\napplied: {n_updated} updated, {n_created} created.")
    print("next: rerun tools/wiki/build_cooccurrence.py to refresh backlinks,")
    print("      and tools/wiki/render_indexes.py to refresh facet INDEXes.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="Path to the source .md file (relative to repo root or absolute)")
    ap.add_argument("--apply", action="store_true", help="Write the proposed changes (default is dry-run)")
    ap.add_argument("--top", type=int, default=20,
                    help="Cap per-facet entity count to keep noise low (default 20)")
    args = ap.parse_args()

    source_path = Path(args.source)
    if not source_path.is_absolute():
        source_path = (Path.cwd() / source_path).resolve()
    if not source_path.exists():
        sys.exit(f"source not found: {source_path}")
    if not source_path.is_file():
        sys.exit(f"source is not a file: {source_path}")

    try:
        source_rel = str(source_path.relative_to(REPO))
    except ValueError:
        sys.exit(f"source is not under the repo: {source_path}")

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"[ingest {mode}] {source_rel}")

    extracted = extract(source_path)
    plan = plan_ingest(extracted, source_rel, top=args.top)
    render_dry_run(plan, extracted)

    if args.apply:
        apply_plan(plan)
    else:
        print()
        print("  (dry-run) re-run with --apply to write these changes.")


if __name__ == "__main__":
    main()
