#!/usr/bin/env python3
"""tools/wiki/retry_with_openai.py — re-run failed bootstrap analyses with OpenAI.

After the parallel Ollama shards finish, ~20% of files have no cache entry
(qwen3.5:122b returned empty output or timed out). This script walks the
same in-scope file list, identifies cache misses, and calls OpenAI
(default: gpt-5-mini) to fill them.

The OpenAI API is much more reliable on structured-JSON tasks than the local
fleet, so this should clean up most of the residual failures cheaply.

Costs real money. Token usage logged to stderr per call by the underlying
helper (`tools/openai/call.py`). For ~80 missing files at ~3-5k input
tokens each, expect ~$1-3 with gpt-5-mini; $5-15 with gpt-5.

Usage:
  python3 tools/wiki/retry_with_openai.py                    # default: gpt-5-mini
  python3 tools/wiki/retry_with_openai.py --model gpt-5      # use the flagship
  python3 tools/wiki/retry_with_openai.py --dry-run          # list missing only
  python3 tools/wiki/retry_with_openai.py --limit 10         # cap files

Constraints:
  - Same in-scope folders as bootstrap.py (writting-projects/, characters/,
    principals/, memory/, sources/, engineering-projects/, root .md).
  - Same chunking discipline (chunk.py) for files >10k tokens.
  - Cache is shared with bootstrap.py — successful retries write to
    tools/wiki/cache/<sha>.json with the SAME JSON shape; the final
    aggregation pass (bootstrap.py --resume) picks them up uniformly.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chunk import chunk_markdown, estimate_tokens, DEFAULT_BUDGET_TOKENS
from bootstrap import (
    REPO, CACHE, file_hash, find_files, parse_json_lenient,
    PROMPT_TEMPLATE, AGGREGATE_TEMPLATE, _deterministic_aggregate, now_iso,
)

OPENAI_HELPER = REPO / "tools" / "openai" / "call.py"
DEFAULT_MODEL = "gpt-5-mini"
RETRY_LOG = REPO / "tools" / "wiki" / "retry-log.md"
TIMEOUT_SECONDS = 900


def call_openai(prompt: str, model: str) -> str:
    """Call tools/openai/call.py; return stdout."""
    cmd = [
        "python3", str(OPENAI_HELPER), "generate",
        "--model", model,
        "--max-tokens", "8000",  # gpt-5* are reasoning models; budget is split between reasoning and visible output
    ]
    # gpt-5* and o-series reject custom temperature; only the default (1) is allowed.
    # Older models (gpt-4*, etc.) accept --temp; tighten if needed.
    if model.startswith("gpt-5") or model.startswith("o"):
        cmd.extend(["--reasoning-effort", "low"])  # this is structured extraction; deep reasoning wastes tokens
    res = subprocess.run(
        cmd,
        input=prompt,
        capture_output=True,
        text=True,
        timeout=TIMEOUT_SECONDS,
    )
    if res.returncode != 0:
        raise RuntimeError(f"openai call failed (code {res.returncode}): {res.stderr.strip()[:300]}")
    # tools/openai/call.py logs token usage to stderr. Capture for the log.
    if res.stderr:
        for line in res.stderr.splitlines():
            if "tokens" in line.lower() or "[" in line:
                pass  # already streamed by helper
    return res.stdout


def analyze_with_openai(path: Path, content: str, model: str) -> dict:
    """Per-file analysis via OpenAI. Same chunking discipline as bootstrap.py."""
    rel = str(path.relative_to(REPO))

    if estimate_tokens(content) <= DEFAULT_BUDGET_TOKENS:
        prompt = PROMPT_TEMPLATE.format(
            path=rel, chunk_n=1, chunk_total=1, content=content
        )
        out = call_openai(prompt, model)
        return parse_json_lenient(out)

    chunks = chunk_markdown(content)
    chunk_outs: list[dict] = []
    for i, c in enumerate(chunks, 1):
        prompt = PROMPT_TEMPLATE.format(
            path=rel, chunk_n=i, chunk_total=len(chunks), content=c
        )
        out = call_openai(prompt, model)
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
        return _deterministic_aggregate(chunk_outs)
    try:
        return parse_json_lenient(call_openai(agg_prompt, model))
    except Exception:
        return _deterministic_aggregate(chunk_outs)


def cache_put(key: str, data) -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE / f"{key}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def cache_has(key: str) -> bool:
    return (CACHE / f"{key}.json").exists()


def log(msg: str) -> None:
    RETRY_LOG.parent.mkdir(parents=True, exist_ok=True)
    with RETRY_LOG.open("a", encoding="utf-8") as f:
        f.write(msg.rstrip() + "\n")
    print(msg, flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=DEFAULT_MODEL,
                    help=f"OpenAI model (default: {DEFAULT_MODEL})")
    ap.add_argument("--dry-run", action="store_true",
                    help="list missing files only, don't call OpenAI")
    ap.add_argument("--limit", type=int, default=0,
                    help="cap files (0 = no cap)")
    args = ap.parse_args()

    files = find_files()
    missing: list[tuple[Path, str, str]] = []
    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        h = file_hash(content)
        if not cache_has(h):
            missing.append((f, content, h))

    log(f"\n## retry run @ {now_iso()}\n")
    log(f"- in-scope total: **{len(files)}**")
    log(f"- cache hits:     {len(files) - len(missing)}")
    log(f"- missing:        **{len(missing)}**")
    log(f"- model:          `{args.model}`")
    if args.dry_run:
        log("- mode: DRY-RUN — listing missing only")
        for f, _, _ in missing[:200]:
            log(f"  · {f.relative_to(REPO)}")
        return

    if args.limit:
        missing = missing[:args.limit]
        log(f"- limit: processing first {len(missing)}")

    successes = 0
    failures: list[tuple[str, str]] = []
    t0 = time.time()
    for i, (f, content, h) in enumerate(missing, 1):
        log(f"  [{i}/{len(missing)}] retrying `{f.relative_to(REPO)}` ({len(content):,} B, ~{estimate_tokens(content)} tok)")
        t1 = time.time()
        try:
            d = analyze_with_openai(f, content, args.model)
            cache_put(h, d)
            successes += 1
            log(f"      ✓ {time.time()-t1:.1f}s · persons={len(d.get('persons_mentioned') or [])} topics={len(d.get('topics') or [])} key-ideas={len(d.get('key_ideas') or [])}")
        except Exception as e:
            failures.append((str(f.relative_to(REPO)), str(e)))
            log(f"      ✗ {e}")

    log(f"\n- retry done in {(time.time()-t0)/60:.1f} min")
    log(f"- recovered: **{successes}**, still failing: **{len(failures)}**")
    if failures:
        log("\n### still failing")
        for rel, err in failures[:50]:
            log(f"- `{rel}` — {err[:200]}")


if __name__ == "__main__":
    main()
