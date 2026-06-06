# tools/wiki/

Scripts that build and maintain the wiki-index layer over the workshop's markdown.

## Files

- **`bootstrap.py`** — first-pass scaffolding. Walks in-scope folders, calls Ollama (qwen3.5:122b) per file under a 16k-context budget, aggregates across files, writes per-facet scaffolds to `wiki/<facet>/<slug>.md`. Cached by file hash → idempotent on re-run. Run via `python3 tools/wiki/bootstrap.py [--smoke|--dry-run|--resume|--limit N|--skip-write]`.
- **`chunk.py`** — splits long markdown into 16k-context-safe chunks for Ollama. Strategy: H2 splits → paragraph splits → sentence splits. Reusable from any wiki-bootstrap-adjacent tool.
- **`validate.py`** — sanity-checker for the wiki tree: broken wikilinks, duplicate slugs, entries with no sources, sources missing on disk. Run after a bootstrap; safe to re-run any time.
- **`bootstrap-log.md`** — append-only run log written by `bootstrap.py`. Records every per-file analysis, every aggregate count, every failure, every "decision needed from Marc" item.
- **`cache/`** — gitignored. Per-file Ollama outputs keyed by SHA-256 of file content. Re-running `bootstrap.py --resume` skips files whose hash matches.

## Scope

In-scope folders (markdown files only):
- `writting-projects/` — except Hugo theme/build dirs (`themes/`, `public/`, `resources/`, `layouts/`, `archetypes/`, `static/`)
- `characters/` — the legati identity files
- `principals/` — human authors (currently just Marc)
- `memory/` — persistent memory system
- `sources/` — raw source materials
- `engineering-projects/` — engineering work folders
- Selected root files: `INDEX.md`, `BACKLOG.md`, `PROJECTS.md`, `TODO.md`, `CLAUDE.md`, `README.md`

Out of scope:
- `inbox/` — Bilby's email/calendar lore (volatile, lane-separate, per Marc's 2026-05-08 instruction)
- `archive/` — preserved but inactive
- `confidential/` — gitignored
- `worldview-draft/` — per-host graph pilot (gitignored, may not exist on every machine)

## Constraints

- **`qwen3.5:122b` only** (per `memory/feedback_ollama_big_guns_only.md`). Both Studios reachable from this host.
- **16k context max** (per `memory/feedback_ollama_context_under_16k.md`). `chunk.py` enforces a working budget of 10k input tokens / call.
- **No git commits** during the bootstrap. The script writes files; Marc commits.

## Output

- `wiki/<facet>/<slug>.md` — per-entry scaffolds. Frontmatter (type, slug, status, dates, source-count) + Summary + Timeline (auto-built from git log over linked sources) + Evolution placeholder + Sources list + Cross-references placeholder.
- `wiki/<facet>/INDEX.md` — alphabetical facet index.
- `wiki/INDEX.md` — top-level wiki map.
- `wiki/keywords/keywords.md` — flat alphabetical keyword reference (terms appearing in ≥2 files, capitalized-token heuristic).

## Re-running

Two reasons to re-run:
1. **Resume after partial completion** — `python3 tools/wiki/bootstrap.py --resume`. Cache hits are free; only newly-changed files get re-analyzed.
2. **Iterate on the prompt or schema** — delete the cache (`rm -rf tools/wiki/cache/`), re-run. Forces fresh Ollama calls for everything.

After any re-run, run `python3 tools/wiki/validate.py` to catch broken links and orphans.

## Maintenance going forward

The bootstrap is a *first pass*. Steady-state maintenance:
- **On-touch** — when a content file under in-scope folders is added / edited / moved, the wiki entries that reference it should also be touched in the same commit. Pre-commit hook at `tools/git-hooks/pre-commit-wiki-check.sh` warns when this discipline slips.
- **Weekly Mycroft sweep** — periodic `validate.py` run, propose updates for entries whose `last-touched` lags.
- **Filling the long tail** — bootstrap leaves many entries as scaffolds (auto-generated frontmatter + sources + timeline; placeholder Summary/Evolution). Mycroft and Agatha fill summaries/evolution incrementally as work touches the underlying files. High-value entries (top projects, named persons, key-ideas) get priority.
