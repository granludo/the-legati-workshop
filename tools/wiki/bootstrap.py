#!/usr/bin/env python3
"""tools/wiki/bootstrap.py — first-pass wiki scaffolding from the repo's markdown.

Walks in-scope folders, calls Ollama per file (chunked if needed) for a JSON
summary + entity extraction, aggregates across files, writes per-facet
scaffolds to `wiki/<facet>/<slug>.md`.

Facets produced:
  - persons     (humans named in the corpus, excluding Marc himself and the legati)
  - projects    (one per writing-project / engineering-project folder)
  - topics      (recurring subject areas)
  - key-ideas   (named intellectual positions / concepts)
  - keywords    (long-tail flat alphabetical reference, single file)

Usage:
  python3 tools/wiki/bootstrap.py --smoke          # 10-file smoke test
  python3 tools/wiki/bootstrap.py                  # full run
  python3 tools/wiki/bootstrap.py --dry-run        # walk + report, no Ollama calls
  python3 tools/wiki/bootstrap.py --resume         # use cache; skip already-analyzed files

Cache: per-file Ollama outputs are cached at tools/wiki/cache/<sha>.json keyed by
file content hash. Idempotent: re-running with --resume re-uses the cache.

Constraints:
  - Ollama context kept under 16k tokens (per feedback_ollama_context_under_16k.md).
    Files exceeding the working budget are chunked via chunk.py.
  - Only qwen3.5:122b (per feedback_ollama_big_guns_only.md).
  - Bootstrap runs on tom-nook-studio (.35) — verified before run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import subprocess
import sys
import time
import unicodedata
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chunk import chunk_markdown, estimate_tokens, DEFAULT_BUDGET_TOKENS

REPO = Path(__file__).resolve().parent.parent.parent
WIKI = REPO / "wiki"
CACHE = REPO / "tools" / "wiki" / "cache"
LOG = REPO / "tools" / "wiki" / "bootstrap-log.md"
OLLAMA_HELPER = REPO / "tools" / "ollama" / "call.py"

INCLUDE_DIRS = ["writting-projects", "characters", "principals", "memory",
                "sources", "engineering-projects"]
EXCLUDE_PATTERN_PARTS = [
    "/themes/", "/public/", "/resources/", "/layouts/",
    "/archetypes/", "/static/", "/.git/", "/node_modules/",
    "/cache/", "/.obsidian/",
]
ROOT_FILES_INCLUDE = ["INDEX.md", "BACKLOG.md", "PROJECTS.md", "TODO.md",
                      "CLAUDE.md", "README.md"]

OLLAMA_MODEL = "qwen3.5:122b"
NUM_CTX = 16000
TIMEOUT_SECONDS = 900

# Names to skip in person extraction (the principal + the legati themselves).
SKIP_PERSON_NAMES = {
    "marc", "marc alier", "marc alier forment", "ludo",
    "agatha", "nagatha", "nagatha christie",
    "mycroft", "mycroft holmes",
    "bilby",
}

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

FILE CONTENT (chunk {chunk_n} of {chunk_total}):
---
{content}
---

JSON output:
"""

AGGREGATE_TEMPLATE = """You are aggregating per-chunk analyses of a single long document into one unified JSON. Combine the chunk outputs below; deduplicate entries; preserve all unique items. Output ONLY the unified JSON, no commentary.

Unified JSON shape (same as per-chunk):

{{
  "summary": "2-3 sentences covering the whole document",
  "persons_mentioned": [...],
  "topics": [...],
  "key_ideas": [...],
  "external_references": [...]
}}

PER-CHUNK OUTPUTS:

{chunks_json}

Unified JSON:
"""


# ---------------------------------------------------------------- utilities --

def slugify(s: str) -> str:
    """ASCII-fold + lowercase + hyphenate."""
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


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def find_files() -> list[Path]:
    files: list[Path] = []
    for d in INCLUDE_DIRS:
        base = REPO / d
        if not base.exists():
            continue
        for p in base.rglob("*.md"):
            sp = "/" + str(p.relative_to(REPO)) + "/"
            if any(x in sp for x in EXCLUDE_PATTERN_PARTS):
                continue
            files.append(p)
    for f in ROOT_FILES_INCLUDE:
        p = REPO / f
        if p.exists():
            files.append(p)
    return sorted(files)


# ----------------------------------------------------------- ollama plumbing --

_OLLAMA_SERVER = None  # set by main(); thread-through for subprocess args


def call_ollama(prompt: str) -> str:
    """Call tools/ollama/call.py with a prompt; return stdout."""
    cmd = ["python3", str(OLLAMA_HELPER)]
    if _OLLAMA_SERVER:
        cmd.extend(["--server", _OLLAMA_SERVER])
    cmd.extend([
        "generate",
        "--model", OLLAMA_MODEL,
        "--num-ctx", str(NUM_CTX),
        "--no-stream",
        "--temp", "0.2",
        "--keep-alive", "24h",
    ])
    res = subprocess.run(
        cmd,
        input=prompt,
        capture_output=True,
        text=True,
        timeout=TIMEOUT_SECONDS,
    )
    if res.returncode != 0:
        raise RuntimeError(f"ollama call failed (code {res.returncode}): {res.stderr.strip()}")
    return res.stdout


def parse_json_lenient(s: str) -> dict:
    """Extract a JSON object from free-form text."""
    s = s.strip()
    s = re.sub(r"^```(?:json)?\s*", "", s)
    s = re.sub(r"\s*```$", "", s)
    start = s.find("{")
    end = s.rfind("}")
    if start < 0 or end <= start:
        raise ValueError(f"no JSON object found in output (len={len(s)})")
    return json.loads(s[start:end + 1])


def analyze_file_content(path: Path, content: str) -> dict:
    """Per-file analysis. Chunks if too big; aggregates chunk outputs."""
    rel = str(path.relative_to(REPO))

    if estimate_tokens(content) <= DEFAULT_BUDGET_TOKENS:
        prompt = PROMPT_TEMPLATE.format(
            path=rel, chunk_n=1, chunk_total=1, content=content
        )
        out = call_ollama(prompt)
        return parse_json_lenient(out)

    chunks = chunk_markdown(content)
    chunk_outs: list[dict] = []
    for i, c in enumerate(chunks, 1):
        prompt = PROMPT_TEMPLATE.format(
            path=rel, chunk_n=i, chunk_total=len(chunks), content=c
        )
        out = call_ollama(prompt)
        try:
            chunk_outs.append(parse_json_lenient(out))
        except Exception as e:
            chunk_outs.append({
                "summary": f"[chunk {i} parse failed: {e}]",
                "persons_mentioned": [], "topics": [],
                "key_ideas": [], "external_references": [],
            })

    agg_prompt = AGGREGATE_TEMPLATE.format(
        chunks_json=json.dumps(chunk_outs, ensure_ascii=False, indent=2)
    )
    if estimate_tokens(agg_prompt) > 13000:
        # Too many chunks — fall back to deterministic aggregation.
        return _deterministic_aggregate(chunk_outs)
    try:
        return parse_json_lenient(call_ollama(agg_prompt))
    except Exception:
        return _deterministic_aggregate(chunk_outs)


def _deterministic_aggregate(chunk_outs: list[dict]) -> dict:
    """Mechanical fallback when Ollama-aggregation fails or is too long."""
    seen_persons: dict[str, str] = {}
    topics: set[str] = set()
    key_ideas: set[str] = set()
    refs: set[str] = set()
    summaries: list[str] = []
    for o in chunk_outs:
        s = (o.get("summary") or "").strip()
        if s and not s.startswith("[chunk"):
            summaries.append(s)
        for p in o.get("persons_mentioned") or []:
            n = (p.get("name") or "").strip()
            if n:
                seen_persons.setdefault(n, p.get("context", ""))
        for t in o.get("topics") or []:
            if isinstance(t, str):
                topics.add(t.strip())
        for k in o.get("key_ideas") or []:
            if isinstance(k, str):
                key_ideas.add(k.strip())
        for r in o.get("external_references") or []:
            if isinstance(r, str):
                refs.add(r.strip())
    return {
        "summary": " ".join(summaries[:2]) or "[chunked file; no aggregate summary available]",
        "persons_mentioned": [{"name": n, "context": c} for n, c in seen_persons.items()],
        "topics": sorted(topics),
        "key_ideas": sorted(key_ideas),
        "external_references": sorted(refs),
    }


# ------------------------------------------------------ git timeline lookup --

_git_cache: dict[Path, list[tuple[str, str]]] = {}

def git_dates_for(path: Path) -> list[tuple[str, str]]:
    """Return [(YYYY-MM-DD, commit-subject)] from oldest to newest for `path`."""
    if path in _git_cache:
        return _git_cache[path]
    try:
        rel = str(path.relative_to(REPO))
        res = subprocess.run(
            ["git", "log", "--reverse", "--follow", "--format=%aI||%s", "--", rel],
            cwd=REPO, capture_output=True, text=True, timeout=30,
        )
        out = []
        for line in res.stdout.strip().split("\n"):
            if "||" not in line:
                continue
            iso, subj = line.split("||", 1)
            out.append((iso[:10], subj))
        _git_cache[path] = out
        return out
    except Exception:
        _git_cache[path] = []
        return []


# --------------------------------------------------------- aggregation pass --

def aggregate(per_file: dict[str, dict]) -> dict:
    """Build per-facet aggregates across all per-file analyses."""
    persons: dict[str, dict] = {}      # slug -> {name, contexts:[(rel, ctx)], sources:set}
    topics: dict[str, dict] = {}       # slug -> {name, sources:set}
    key_ideas: dict[str, dict] = {}    # slug -> {name, sources:set}
    keywords: dict[str, set[str]] = {}  # term -> sources

    for rel, d in per_file.items():
        for p in d.get("persons_mentioned") or []:
            name = (p.get("name") or "").strip()
            if not name:
                continue
            if name.lower() in SKIP_PERSON_NAMES:
                continue
            sl = slugify(name)
            if not sl:
                continue
            entry = persons.setdefault(sl, {"name": name, "contexts": [], "sources": set()})
            entry["contexts"].append((rel, (p.get("context") or "").strip()))
            entry["sources"].add(rel)
            if len(name) > len(entry["name"]):
                entry["name"] = name

        for t in d.get("topics") or []:
            if not isinstance(t, str): continue
            t = t.strip()
            if not t: continue
            sl = slugify(t)
            if not sl: continue
            entry = topics.setdefault(sl, {"name": t, "sources": set()})
            entry["sources"].add(rel)

        for k in d.get("key_ideas") or []:
            if not isinstance(k, str): continue
            k = k.strip()
            if not k: continue
            sl = slugify(k)
            if not sl: continue
            entry = key_ideas.setdefault(sl, {"name": k, "sources": set()})
            entry["sources"].add(rel)

    return {"persons": persons, "topics": topics, "key_ideas": key_ideas,
            "keywords": keywords, "per_file": per_file}


# ------------------------------------------------------------ wiki writing --

ENTRY_TEMPLATE = """---
type: {type}
slug: {slug}
name: {name}
status: active
first-seen: {first_seen}
last-touched: {last_touched}
sources-count: {sources_count}
---

## Summary

{summary}

## Timeline

{timeline}

## Evolution

{evolution_placeholder}

## Sources

{sources}

## Cross-references

{crossrefs}
"""


def render_entry(facet: str, slug: str, entry: dict, per_file: dict) -> str:
    name = entry["name"]
    sources = sorted(entry.get("sources", set()))

    # Timeline: union of git-log dates across the linked sources.
    dates: list[tuple[str, str, str]] = []   # (date, source-rel, subject)
    for rel in sources:
        path = REPO / rel
        for d, subj in git_dates_for(path):
            dates.append((d, rel, subj))
    dates.sort(key=lambda x: x[0])
    if dates:
        first_seen = dates[0][0]
        last_touched = dates[-1][0]
    else:
        first_seen = last_touched = datetime.now().date().isoformat()

    timeline_lines = []
    seen_dates: set[tuple[str, str]] = set()
    for d, rel, subj in dates[:30]:
        key = (d, rel)
        if key in seen_dates:
            continue
        seen_dates.add(key)
        timeline_lines.append(f"- {d} — [[{rel}]] · {subj}")
    timeline_md = "\n".join(timeline_lines) if timeline_lines else "- *(no git history)*"

    sources_md_lines = []
    for rel in sources:
        ctx_hint = ""
        if facet == "persons":
            for ctx_rel, ctx in entry.get("contexts", []):
                if ctx_rel == rel and ctx:
                    ctx_hint = f" — {ctx}"
                    break
        sources_md_lines.append(f"- [[{rel}]]{ctx_hint}")
    sources_md = "\n".join(sources_md_lines)

    summary = "*[scaffold — fill on next pass]*"
    if facet == "persons":
        # Best one-line context across files.
        best = ""
        for _, c in entry.get("contexts", []):
            if c and len(c) > len(best):
                best = c
        if best:
            summary = best

    crossrefs_md = "*[populate as connections accrete]*"

    return ENTRY_TEMPLATE.format(
        type=facet[:-1] if facet.endswith("s") else facet,
        slug=slug, name=name,
        first_seen=first_seen, last_touched=last_touched,
        sources_count=len(sources),
        summary=summary,
        timeline=timeline_md,
        evolution_placeholder="*[open threads / next moves to fill]*",
        sources=sources_md,
        crossrefs=crossrefs_md,
    )


def render_project_entry(project_dir: Path, per_file: dict) -> tuple[str, str]:
    rel = str(project_dir.relative_to(REPO))
    slug = slugify(project_dir.name)
    name = project_dir.name

    sources = []
    summaries = []
    for f_rel, d in per_file.items():
        if f_rel.startswith(rel + "/") or f_rel == rel:
            sources.append(f_rel)
            s = (d.get("summary") or "").strip()
            if s and not s.startswith("[") and len(summaries) < 3:
                summaries.append(s)
    if not sources:
        return None, None

    dates: list[tuple[str, str]] = []
    for r in sources:
        for d, subj in git_dates_for(REPO / r):
            dates.append((d, subj))
    dates.sort(key=lambda x: x[0])
    first_seen = dates[0][0] if dates else datetime.now().date().isoformat()
    last_touched = dates[-1][0] if dates else first_seen

    timeline_lines = []
    seen: set[str] = set()
    for d, subj in dates[:10]:
        if d in seen:
            continue
        seen.add(d)
        timeline_lines.append(f"- {d} — {subj}")
    timeline_md = "\n".join(timeline_lines) or "- *(no git history)*"

    sources_md = "\n".join(f"- [[{r}]]" for r in sorted(sources))
    summary = " ".join(summaries) or "*[scaffold — fill on next pass]*"

    body = ENTRY_TEMPLATE.format(
        type="project", slug=slug, name=name,
        first_seen=first_seen, last_touched=last_touched,
        sources_count=len(sources),
        summary=summary, timeline=timeline_md,
        evolution_placeholder="*[open threads / next moves to fill]*",
        sources=sources_md,
        crossrefs="*[populate as connections accrete]*",
    )
    return slug, body


def write_facet_index(facet: str, entries: dict) -> None:
    """Write wiki/<facet>/INDEX.md as alphabetical list."""
    path = WIKI / facet / "INDEX.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# wiki/{facet}/ — INDEX",
        "",
        f"Generated by `tools/wiki/bootstrap.py` at {now_iso()}.",
        f"Total entries: **{len(entries)}**.",
        "",
        "| Slug | Name | Sources |",
        "| --- | --- | --- |",
    ]
    for slug in sorted(entries):
        e = entries[slug]
        if isinstance(e, dict):
            name = e.get("name", slug)
            count = len(e.get("sources", []))
        else:
            name = slug
            count = "-"
        lines.append(f"| [[{slug}]] | {name} | {count} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_keywords_flat(per_file: dict) -> None:
    """Single flat keywords file: alphabetical lookup of capitalized terms."""
    counter: dict[str, set[str]] = {}
    cap_re = re.compile(r"\b[A-Z][A-Za-z0-9]{2,}(?:\s+[A-Z][A-Za-z0-9]+)*\b")
    for rel, d in per_file.items():
        try:
            content = (REPO / rel).read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for m in cap_re.findall(content):
            if len(m) < 3:
                continue
            counter.setdefault(m, set()).add(rel)

    path = WIKI / "keywords" / "keywords.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# wiki/keywords/keywords.md",
        "",
        f"Auto-generated alphabetical keyword reference. {len(counter)} terms.",
        f"Generated {now_iso()}.",
        "",
    ]
    for term in sorted(counter, key=str.casefold):
        srcs = counter[term]
        if len(srcs) < 2:
            continue
        lines.append(f"- **{term}** ({len(srcs)} files)")
        for s in sorted(srcs)[:5]:
            lines.append(f"  - [[{s}]]")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ----------------------------------------------------------------- driver --

def log_append(msg: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(msg.rstrip() + "\n")
    print(msg, flush=True)


def smoke_pick(files: list[Path], n: int = 10) -> list[Path]:
    """Pick a balanced ~10-file subset spanning facets."""
    pools = {
        "memory": [f for f in files if "/memory/" in str(f)],
        "characters": [f for f in files if "/characters/" in str(f)],
        "principals": [f for f in files if "/principals/" in str(f)],
        "engineering": [f for f in files if "/engineering-projects/" in str(f)],
        "writting": [f for f in files if "/writting-projects/" in str(f)],
        "sources": [f for f in files if "/sources/" in str(f)],
    }
    rnd = random.Random(42)
    pick: list[Path] = []
    for k, pool in pools.items():
        if not pool:
            continue
        sample = rnd.sample(pool, min(2, len(pool)))
        pick.extend(sample)
    return pick[:n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="run on ~10 sampled files")
    ap.add_argument("--dry-run", action="store_true", help="walk + report only")
    ap.add_argument("--resume", action="store_true", help="use cache where present")
    ap.add_argument("--skip-write", action="store_true", help="don't write wiki entries")
    ap.add_argument("--limit", type=int, default=0, help="cap files (0 = no cap)")
    ap.add_argument("--server", type=str, default=None,
                    help="Ollama server URL (e.g. http://192.168.1.35:11434). Default: auto-discover via call.py.")
    ap.add_argument("--shard", type=str, default=None,
                    help="parallel shard 'i/n' — e.g. '0/2' or '1/2' for two-process split. "
                         "Splits by SHA-256 hash of the file's relative path.")
    ap.add_argument("--analysis-only", action="store_true",
                    help="run analysis (Ollama calls) but don't aggregate or write wiki/. "
                         "Use when running parallel shards: each shard does analysis, then a final aggregation pass writes wiki/.")
    args = ap.parse_args()

    global _OLLAMA_SERVER
    _OLLAMA_SERVER = args.server

    files = find_files()

    if args.shard:
        try:
            i_str, n_str = args.shard.split("/")
            shard_i, shard_n = int(i_str), int(n_str)
        except Exception:
            print(f"bad --shard '{args.shard}'; expected 'i/n' (e.g. '0/2')", file=sys.stderr)
            sys.exit(1)
        files = [f for f in files
                 if int(hashlib.sha256(str(f.relative_to(REPO)).encode()).hexdigest()[:8], 16) % shard_n == shard_i]
        log_append(f"- shard {shard_i}/{shard_n}: {len(files)} files for this shard (server: {args.server or 'auto'})")
    log_append(f"\n## bootstrap run @ {now_iso()}\n")
    log_append(f"- in-scope files: **{len(files)}**")
    log_append(f"- mode: {'SMOKE' if args.smoke else ('DRY-RUN' if args.dry_run else 'FULL')}")

    if args.smoke:
        files = smoke_pick(files, n=10)
        log_append(f"- smoke-test files ({len(files)}):")
        for f in files:
            log_append(f"  - {f.relative_to(REPO)}")

    if args.limit:
        files = files[:args.limit]

    if args.dry_run:
        for f in files[:50]:
            log_append(f"  · {f.relative_to(REPO)} ({f.stat().st_size:,} B)")
        return

    per_file: dict[str, dict] = {}
    failures: list[tuple[str, str]] = []

    t0 = time.time()
    for i, f in enumerate(files, 1):
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            failures.append((str(f.relative_to(REPO)), f"read: {e}"))
            continue

        h = file_hash(content)
        cached = cache_get(h) if args.resume else None
        if cached:
            per_file[str(f.relative_to(REPO))] = cached
            if i % 25 == 0 or i == len(files):
                log_append(f"  [{i}/{len(files)}] cache-hit `{f.relative_to(REPO)}`")
            continue

        log_append(f"  [{i}/{len(files)}] analyzing `{f.relative_to(REPO)}` ({len(content):,} B, ~{estimate_tokens(content)} tok)")
        try:
            t1 = time.time()
            d = analyze_file_content(f, content)
            cache_put(h, d)
            per_file[str(f.relative_to(REPO))] = d
            log_append(f"      ✓ {time.time()-t1:.1f}s · persons={len(d.get('persons_mentioned') or [])} topics={len(d.get('topics') or [])} key-ideas={len(d.get('key_ideas') or [])}")
        except Exception as e:
            failures.append((str(f.relative_to(REPO)), str(e)))
            log_append(f"      ✗ {e}")

    log_append(f"\n- analysis done in {(time.time()-t0)/60:.1f} min")
    log_append(f"- analyzed: **{len(per_file)}**, failed: **{len(failures)}**")

    if args.skip_write:
        log_append("- --skip-write set; not writing wiki/")
        return

    log_append("\n### aggregating across files")
    agg = aggregate(per_file)
    log_append(f"- unique persons:    {len(agg['persons'])}")
    log_append(f"- unique topics:     {len(agg['topics'])}")
    log_append(f"- unique key-ideas:  {len(agg['key_ideas'])}")

    log_append("\n### writing wiki entries")
    for slug, e in agg["persons"].items():
        e["sources"] = sorted(e["sources"])
        body = render_entry("persons", slug, e, per_file)
        path = WIKI / "persons" / f"{slug}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    write_facet_index("persons", agg["persons"])
    log_append(f"- wrote {len(agg['persons'])} wiki/persons/ entries")

    for slug, e in agg["topics"].items():
        e["sources"] = sorted(e["sources"])
        body = render_entry("topics", slug, e, per_file)
        path = WIKI / "topics" / f"{slug}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    write_facet_index("topics", agg["topics"])
    log_append(f"- wrote {len(agg['topics'])} wiki/topics/ entries")

    for slug, e in agg["key_ideas"].items():
        e["sources"] = sorted(e["sources"])
        body = render_entry("key-ideas", slug, e, per_file)
        path = WIKI / "key-ideas" / f"{slug}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    write_facet_index("key-ideas", agg["key_ideas"])
    log_append(f"- wrote {len(agg['key_ideas'])} wiki/key-ideas/ entries")

    project_dirs = []
    for top in ["writting-projects", "engineering-projects"]:
        for child in (REPO / top).iterdir():
            if child.is_dir() and not child.name.startswith("."):
                project_dirs.append(child)
            if child.is_dir():
                # one level deeper for nested projects (fib/asmi)
                for sub in child.iterdir():
                    if sub.is_dir() and (sub / "BACKLOG.md").exists():
                        project_dirs.append(sub)

    project_entries = {}
    for pd in project_dirs:
        slug, body = render_project_entry(pd, per_file)
        if not slug:
            continue
        project_entries[slug] = {"name": pd.name, "sources": []}
        path = WIKI / "projects" / f"{slug}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    write_facet_index("projects", project_entries)
    log_append(f"- wrote {len(project_entries)} wiki/projects/ entries")

    write_keywords_flat(per_file)
    log_append(f"- wrote wiki/keywords/keywords.md")

    write_top_index(agg, project_entries)

    if failures:
        log_append(f"\n### failures ({len(failures)})")
        for rel, err in failures[:50]:
            log_append(f"- `{rel}` — {err}")

    log_append(f"\n### done @ {now_iso()}\n")


def write_top_index(agg: dict, project_entries: dict) -> None:
    path = WIKI / "INDEX.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    body = f"""# wiki/ — top-level INDEX

Auto-generated by `tools/wiki/bootstrap.py` at {now_iso()}.

## Facets

| Facet | Count | Index |
| --- | --- | --- |
| Persons | {len(agg['persons'])} | [[persons/INDEX]] |
| Projects | {len(project_entries)} | [[projects/INDEX]] |
| Topics | {len(agg['topics'])} | [[topics/INDEX]] |
| Key ideas | {len(agg['key_ideas'])} | [[key-ideas/INDEX]] |
| Keywords | (alphabetical flat file) | [[keywords/keywords]] |

## How to use this wiki

- Per-entry files at `wiki/<facet>/<slug>.md` carry: summary, timeline-of-additions (built from git log of linked sources), evolution placeholder (humans fill), sources list, cross-references.
- The bootstrap pass produces **scaffolds**: timelines and source lists are auto-generated; summaries are scaffolded for low-density entries and pre-filled for persons (best context line).
- High-value entries (top projects, top persons, named key-ideas) are the ones to fill in by hand or by Agatha.
- Maintenance: per `feedback_index_maintenance.md` + the pre-commit hook at `tools/git-hooks/`, when a content file changes, the wiki entries that reference it should also touch in the same commit.

## Bootstrap log

See [`../tools/wiki/bootstrap-log.md`](../tools/wiki/bootstrap-log.md).
"""
    path.write_text(body, encoding="utf-8")


if __name__ == "__main__":
    main()
