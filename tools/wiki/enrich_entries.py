#!/usr/bin/env python3
"""tools/wiki/enrich_entries.py — fill scaffold Summary sections via DS4.

For each entry in wiki/<facet>/ whose Summary is still the bootstrap
placeholder ("*[scaffold — fill on next pass]*" / empty), build a context
from the per-source cached analyses and ask DS4 + DeepSeek V4 Flash to
produce a 2-3 paragraph matter-of-fact summary. Replace the Summary
section in-place.

Per `memory/reference_ds4_server.md`:
  - English output only (DS4 is ES/EN; CA stays on Claude/OpenAI).
  - reasoning_effort=low keeps the latency in check for the bulk pass.
  - Same system prompt across all calls so DS4's SHA1 KV cache reuses the prefix.

Resumable: each enriched entry writes its new Summary section to disk
immediately. Re-running with --resume skips entries whose Summary already
looks enriched.

Usage:
  python3 tools/wiki/enrich_entries.py topics --smoke         # 5 entries
  python3 tools/wiki/enrich_entries.py topics                 # full pass
  python3 tools/wiki/enrich_entries.py key-ideas
  python3 tools/wiki/enrich_entries.py topics --limit 50 --resume
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
WIKI = REPO / "wiki"
CACHE = REPO / "tools" / "wiki" / "cache"
DS4_HELPER = REPO / "tools" / "ds4" / "call.py"
LOG = REPO / "tools" / "wiki" / "enrich-log.md"

DS4_MODEL = "deepseek-v4-flash"
MAX_TOKENS = 800
TIMEOUT_SECONDS = 600

SCAFFOLD_MARKERS = (
    "*[scaffold — fill on next pass]*",
    "*[scaffold - fill on next pass]*",
    "*[awaiting next pass]*",
)

SYSTEM_PROMPT = """You are a precise, terse technical writer producing wiki entries for a personal research repository.

Output a 2-3 paragraph matter-of-fact summary of the requested topic / idea / person, in ENGLISH, based on the context provided.

Style rules:
- Plain language. No marketing voice. No bullet lists in the body.
- No hedging language ("it may", "it could"). State what the sources say.
- No "this entry covers" / "this summary describes" / meta-talk.
- 2-3 paragraphs, ~80-180 words total.
- Open with what the thing IS (definition or core claim), then how it shows up across the sources, then any tensions or open questions visible in the corpus.
- If the context is too thin to summarize, output exactly: "INSUFFICIENT_CONTEXT" and nothing else.

Output the summary text directly. No headers, no preamble, no "Summary:" label."""

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def now_iso() -> str:
    from datetime import datetime
    return datetime.now().isoformat(timespec="seconds")


def log(msg: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(msg.rstrip() + "\n")
    print(msg, flush=True)


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    out = {}
    in_list_key = None
    for line in m.group(1).splitlines():
        if line.startswith("  - ") and in_list_key:
            out.setdefault(in_list_key, []).append(line[4:].strip())
            continue
        in_list_key = None
        if ":" in line:
            k, v = line.split(":", 1)
            v = v.strip()
            if v == "":
                in_list_key = k.strip()
                out[in_list_key] = []
            else:
                out[k.strip()] = v
    return out


def parse_section(text: str, header: str) -> str:
    """Return the body of `## <header>` section (everything until next `## `)."""
    in_section = False
    out: list[str] = []
    for line in text.splitlines():
        if line.strip() == f"## {header}":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            out.append(line)
    return "\n".join(out).strip()


def parse_sources_list(text: str) -> list[str]:
    in_section = False
    out = []
    for line in text.splitlines():
        if line.strip() == "## Sources":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            m = re.search(r"\[\[([^\]\|\#]+)\]\]", line)
            if m:
                out.append(m.group(1).strip())
    return out


def is_scaffold(summary: str) -> bool:
    s = summary.strip()
    if not s:
        return True
    for marker in SCAFFOLD_MARKERS:
        if marker in s:
            return True
    # Very short and starts with * — likely a placeholder
    if len(s) < 40 and s.startswith("*"):
        return True
    return False


def load_cache_index() -> dict[str, dict]:
    """Map repo-relative file path -> cached analysis (by file-content hash).

    The cache is keyed by sha256 of file CONTENT, not by path. To look up by
    path we must hash each source file ourselves at lookup time.
    """
    return {}  # we hash on demand; see source_summary_for


def source_summary_for(rel_path: str) -> str:
    """Return the cached summary for `rel_path`, or '' if not cached."""
    p = REPO / rel_path
    if not p.exists():
        return ""
    try:
        content = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""
    h = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
    cache_file = CACHE / f"{h}.json"
    if not cache_file.exists():
        return ""
    try:
        d = json.loads(cache_file.read_text(encoding="utf-8"))
        return (d.get("summary") or "").strip()
    except Exception:
        return ""


def build_context(name: str, slug: str, facet: str, sources: list[str]) -> str:
    """Compose the user prompt for DS4."""
    facet_label = {"topics": "topic", "key-ideas": "key idea (intellectual position or concept)",
                   "persons": "person"}.get(facet, facet)
    lines = [
        f"Write the wiki summary for this {facet_label}:",
        "",
        f"  Name: {name}",
        f"  Slug: {slug}",
        "",
        f"It is mentioned in {len(sources)} source(s). Per-source summaries from the corpus follow.",
        "",
    ]
    included = 0
    for rel in sources[:12]:
        s = source_summary_for(rel)
        if not s:
            continue
        s = s.replace("\n", " ").strip()
        if len(s) > 600:
            s = s[:600] + "..."
        lines.append(f"  [{rel}]")
        lines.append(f"    {s}")
        lines.append("")
        included += 1
    if included == 0:
        lines.append("  (no cached summaries available for the linked sources)")
    elif len(sources) > 12:
        lines.append(f"  ...and {len(sources) - 12} more sources not shown")
    lines.append("")
    lines.append("Write the summary now.")
    return "\n".join(lines)


def call_ds4(system: str, user: str) -> str:
    cmd = [
        "python3", str(DS4_HELPER), "generate",
        "--model", DS4_MODEL,
        "--system", system,
        "--max-tokens", str(MAX_TOKENS),
        "--temp", "0.3",
        "--reasoning-effort", "low",
    ]
    res = subprocess.run(
        cmd, input=user, capture_output=True, text=True, timeout=TIMEOUT_SECONDS,
    )
    if res.returncode != 0:
        raise RuntimeError(f"ds4 call failed (code {res.returncode}): {res.stderr.strip()[:300]}")
    return res.stdout.strip()


def replace_summary(text: str, new_summary: str) -> str:
    """Replace the body of `## Summary` with new_summary. Leave rest as-is."""
    lines = text.splitlines()
    out: list[str] = []
    in_section = False
    written = False
    for line in lines:
        if line.strip() == "## Summary":
            in_section = True
            written = True
            out.append(line)
            out.append("")
            out.append(new_summary.strip())
            out.append("")
            continue
        if in_section:
            if line.startswith("## "):
                in_section = False
                out.append(line)
            # else: skip old summary content
        else:
            out.append(line)
    if not written:
        # No existing Summary section — append one
        if out and out[-1].strip():
            out.append("")
        out.append("## Summary")
        out.append("")
        out.append(new_summary.strip())
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("facet", choices=["topics", "key-ideas", "persons"])
    ap.add_argument("--smoke", action="store_true", help="enrich ~5 entries")
    ap.add_argument("--limit", type=int, default=0, help="cap entries (0 = no cap)")
    ap.add_argument("--resume", action="store_true",
                    help="skip entries whose Summary is not a scaffold")
    ap.add_argument("--max-summary-length", type=int, default=0,
                    help="treat summaries shorter than N chars as scaffolds "
                         "(default 0 = only literal scaffold markers count)")
    ap.add_argument("--only-roles", action="store_true",
                    help="restrict to entries whose frontmatter has a roles: "
                         "field (currently only persons get role tags)")
    args = ap.parse_args()

    facet_dir = WIKI / args.facet
    if not facet_dir.exists():
        print(f"ERROR: {facet_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    def is_short_or_scaffold(s: str) -> bool:
        if is_scaffold(s):
            return True
        if args.max_summary_length and len(s.strip()) < args.max_summary_length:
            return True
        return False

    candidates: list[Path] = []
    skipped_already_enriched = 0
    skipped_no_roles = 0
    for p in sorted(facet_dir.glob("*.md")):
        if p.name == "INDEX.md":
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        if args.only_roles and "\nroles:\n" not in text and not text.startswith("roles:\n"):
            skipped_no_roles += 1
            continue
        summary = parse_section(text, "Summary")
        if args.resume and not is_short_or_scaffold(summary):
            skipped_already_enriched += 1
            continue
        if is_short_or_scaffold(summary):
            candidates.append(p)

    log(f"\n## enrich run @ {now_iso()}\n")
    log(f"- facet: {args.facet}")
    if args.only_roles:
        log(f"- filter: --only-roles (entries without `roles:` skipped: {skipped_no_roles})")
    if args.max_summary_length:
        log(f"- filter: --max-summary-length={args.max_summary_length}")
    log(f"- scaffold candidates: **{len(candidates)}**")
    log(f"- already enriched (skipped): {skipped_already_enriched}")

    if args.smoke:
        candidates = candidates[:5]
        log(f"- smoke mode: first {len(candidates)}")
    if args.limit:
        candidates = candidates[:args.limit]
        log(f"- limit: {len(candidates)}")

    successes = 0
    failures = 0
    insufficient = 0
    t0 = time.time()
    for i, p in enumerate(candidates, 1):
        text = p.read_text(encoding="utf-8", errors="ignore")
        fm = parse_frontmatter(text)
        name = fm.get("name", p.stem).strip('"').strip("'")
        sources = parse_sources_list(text)
        if not sources:
            log(f"  [{i}/{len(candidates)}] skip `{p.name}` (no sources)")
            continue
        user_prompt = build_context(name, p.stem, args.facet, sources)
        try:
            t1 = time.time()
            new_summary = call_ds4(SYSTEM_PROMPT, user_prompt)
            dt = time.time() - t1
        except Exception as e:
            failures += 1
            log(f"  [{i}/{len(candidates)}] ✗ `{p.name}` — {e}")
            continue
        if new_summary.strip() == "INSUFFICIENT_CONTEXT":
            insufficient += 1
            log(f"  [{i}/{len(candidates)}] ↷ `{p.name}` — insufficient context (kept scaffold)")
            continue
        new_text = replace_summary(text, new_summary)
        p.write_text(new_text, encoding="utf-8")
        successes += 1
        log(f"  [{i}/{len(candidates)}] ✓ `{p.name}` ({dt:.1f}s, {len(new_summary)} chars)")

    log(f"\n- done in {(time.time()-t0)/60:.1f} min")
    log(f"- enriched: **{successes}**, failed: **{failures}**, insufficient: **{insufficient}**")


if __name__ == "__main__":
    main()
