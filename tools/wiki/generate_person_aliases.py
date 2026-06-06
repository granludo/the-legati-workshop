#!/usr/bin/env python3
"""tools/wiki/generate_person_aliases.py — fill alias variants for person entries.

For each wiki/persons/<slug>.md, ask qwen3.5:122b on Studio64 to enumerate
common name variants (initials, abbreviations, alternate spellings, partial
forms) and write them into the entry's `aliases:` frontmatter.

Aliases help downstream:
  · classify_persons.py contact detection — Bilby's `inbox/lore/persons/`
    slugs may use a variant the wiki entry doesn't yet list as alias
  · /add-source ingest matching — avoids creating duplicate person entries
    (the `juan-antonio-pereira` ↔ `juanan-pereira` problem)
  · slug-variant detector — alias-aware merge suggestions

Re-runnable. Idempotent: skips entries that already have ≥2 aliases.

Routes through DS4 (tom-nook 0.0.0.0:8000) + DeepSeek V4 Flash with
reasoning_effort=low — short structured outputs, KV cache reuses the
system-prompt prefix across calls. Each call ~5-15s. ~1100 persons →
~2-3h runtime.

History: previously routed through Studio64's Ollama qwen3.5:122b, which
hit ~50% TimeoutExpired rate on the 180s timeout (~50h projected runtime).
Moved to DS4 on 2026-05-13.

Usage:
  python3 tools/wiki/generate_person_aliases.py
  python3 tools/wiki/generate_person_aliases.py --limit 50    # cap
  python3 tools/wiki/generate_person_aliases.py --only-roles  # role-tagged
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
WIKI_PERSONS = REPO / "wiki" / "persons"
DS4_HELPER = REPO / "tools" / "ds4" / "call.py"
DS4_MODEL = "deepseek-chat"  # non-thinking; we want raw JSON, not reasoning traces
LOG_PATH = REPO / "tools" / "wiki" / "alias-gen-log.md"

SYSTEM_PROMPT = """You enumerate the common name variants for a person's name in academic citation contexts. Output ONLY a single JSON object — no markdown fences, no commentary:

{"aliases": ["variant 1", "variant 2", ...]}

Rules:
- Include: full name; "Last, First Middle"; "F. Last"; "Last F"; "First Last"; common nicknames (only if widely used in academic literature); hyphen / accent variants; partial forms ("Last" alone if distinctive).
- Exclude: the input name itself (it's the canonical); typos; speculative variants you can't verify.
- 2-6 aliases is the right range. If the name has no plausible variants (very short / single-word / already minimal), return {"aliases": []}.
- Preserve Catalan/Spanish/Catalan diacritics where appropriate.
- Do not invent middle names or institutional affiliations.
"""

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict, str, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, "", text
    block = m.group(1)
    body = text[m.end():]
    fm: dict = {}
    aliases: list[str] = []
    in_aliases = False
    for line in block.splitlines():
        if line.startswith("aliases:"):
            in_aliases = True
            continue
        if in_aliases and re.match(r"^\s*-\s+", line):
            aliases.append(re.sub(r"^\s*-\s+", "", line).strip().strip('"').strip("'"))
            continue
        in_aliases = False
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"').strip("'")
    fm["aliases"] = aliases
    return fm, block, body


def call_model(system: str, user: str) -> str:
    """Route to DS4 (tom-nook). System + user combined into one prompt
    because the helper's --system flag treats values as filepath-or-text
    and long multi-line strings trigger OSError on macOS path-length check.
    Token-identical prefix → DS4's SHA1 KV cache hits across calls anyway."""
    combined = f"{system}\n\nINPUT NAME:\n{user}\n\nJSON output:"
    proc = subprocess.run(
        ["python3", str(DS4_HELPER),
         "generate",
         "--model", DS4_MODEL,
         "--temp", "0.2",
         "--max-tokens", "300"],
        input=combined,
        text=True,
        capture_output=True,
        timeout=90,
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


def render_frontmatter(block: str, aliases: list[str]) -> str:
    """Insert / replace aliases: block in the frontmatter."""
    lines = block.split("\n")
    out: list[str] = []
    i = 0
    aliases_lines = ["aliases:"] + [f"  - {a}" for a in aliases]
    written = False
    while i < len(lines):
        line = lines[i]
        if line.startswith("aliases:"):
            out.extend(aliases_lines)
            written = True
            i += 1
            while i < len(lines) and re.match(r"^\s+-\s+", lines[i]):
                i += 1
            continue
        out.append(line)
        i += 1
    if not written and aliases:
        out.extend(aliases_lines)
    return "---\n" + "\n".join(out) + "\n---\n"


def log(msg: str):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg, flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="cap N entries")
    ap.add_argument("--only-roles", action="store_true",
                    help="only process entries with a roles: frontmatter field")
    ap.add_argument("--force", action="store_true",
                    help="re-generate even for entries already with ≥2 aliases")
    args = ap.parse_args()

    log(f"\n## alias-gen run @ {time.strftime('%Y-%m-%dT%H:%M:%S')}\n")

    candidates: list[Path] = []
    for p in sorted(WIKI_PERSONS.glob("*.md")):
        if p.name == "INDEX.md":
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        fm, _, _ = parse_frontmatter(text)
        if args.only_roles and not fm.get("roles"):
            # roles field not parsed by minimal parser; check via grep
            if "\nroles:\n" not in text and not text.startswith("roles:\n"):
                continue
        if not args.force and len(fm.get("aliases", [])) >= 2:
            continue
        candidates.append(p)

    log(f"- candidates: {len(candidates)} (limit={args.limit})")
    if args.limit:
        candidates = candidates[: args.limit]

    successes = 0
    failures = 0
    empties = 0
    t0 = time.time()
    save_log_every = 20
    for i, p in enumerate(candidates, 1):
        text = p.read_text(encoding="utf-8", errors="ignore")
        fm, block, body = parse_frontmatter(text)
        name = fm.get("name", p.stem)
        try:
            t1 = time.time()
            raw = call_model(SYSTEM_PROMPT, name)
            data = parse_json_lenient(raw)
            new_aliases = [a.strip() for a in (data.get("aliases") or []) if a.strip()]
            # Dedupe + drop the canonical itself
            new_aliases = [a for a in new_aliases if a.lower() != name.lower()]
            seen = set()
            new_aliases = [a for a in new_aliases if not (a.lower() in seen or seen.add(a.lower()))]
            dt = time.time() - t1
        except (RuntimeError, ValueError, subprocess.TimeoutExpired, json.JSONDecodeError) as e:
            failures += 1
            log(f"  [{i}/{len(candidates)}] ✗ {p.name}: {type(e).__name__}")
            continue
        if not new_aliases:
            empties += 1
            log(f"  [{i}/{len(candidates)}] ↷ {p.name} — no aliases ({dt:.1f}s)")
            continue
        # Merge with existing aliases, dedupe
        existing = fm.get("aliases", [])
        merged = list(existing) + [a for a in new_aliases if a.lower() not in {e.lower() for e in existing}]
        new_block = render_frontmatter(block, merged)
        p.write_text(new_block + body, encoding="utf-8")
        successes += 1
        log(f"  [{i}/{len(candidates)}] ✓ {p.name} +{len(new_aliases)} aliases ({dt:.1f}s)")
        if i % save_log_every == 0:
            elapsed = time.time() - t0
            rate = i / elapsed
            eta = (len(candidates) - i) / rate / 60
            log(f"  progress: {i}/{len(candidates)} (eta {eta:.1f}m)")

    log(f"\n- done in {(time.time()-t0)/60:.1f} min")
    log(f"- successes: {successes}, empty: {empties}, failures: {failures}")


if __name__ == "__main__":
    main()
