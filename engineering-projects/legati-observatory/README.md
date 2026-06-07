---
type: project-folder
project: Legati Observatory
status: working — portable core + Claude Code adapter
---

# Legati Observatory

A **portable, static, stigmergic** observability + light-coordination layer for a workshop's parallel AI sessions (the *legati* — your named agents). When several agent instances run against the same repo at once, this tells you **who is live, what they're doing, who is orchestrating whom, and what it cost** — and gives them a way to **not step on each other** when writing shared files.

**Why build your own** instead of installing a third-party dashboard: it stays portable across harnesses (not coupled to one tool), static (no webserver, no cloud-DB trust surface), aligned to the coordination problem that actually bites (parallel instances racing on the same file), and legible enough to double as teaching material. It is a worked example of **stigmergy over orchestration**: the agents coordinate **with no central orchestrator** — by leaving traces in shared files (presence + advisory-lock files as pheromone trails) and reading the environment's state. The repository is the termite mound.

## How it works (three layers, one firewall)

```
 harness hooks  ──►  adapters/<harness>/  ──►  event schema  ──►  .observatory/  ──►  obs render  ──►  dashboard
 (Claude Code,        (the only harness-       (the contract,      (portable core:      (static)         (.md / .html)
  Codex, …)            aware code)              ADAPTERS.md)        events+presence+locks)
```

The core (`obs.py` + renderers) knows nothing about any harness. To support a new harness you write **one** adapter that emits the same event schema; nothing else changes. See [`DESIGN.md`](DESIGN.md) and [`ADAPTERS.md`](ADAPTERS.md).

## Files

| File | What |
|---|---|
| [`obs.py`](obs.py) | The portable core CLI — `emit` · `task` · `heartbeat` · `who` · `agent` · `lock {acquire,check,release}` · `render`. Pure stdlib, Python 3.9+. |
| [`DESIGN.md`](DESIGN.md) | The design — the portability firewall, event schema, file layout, lock protocol, renderers. |
| [`ADAPTERS.md`](ADAPTERS.md) | The portability contract: event schema + worked Claude Code hook config + how to port to another harness. |
| [`adapters/claude-code/hook-handler.py`](adapters/claude-code/hook-handler.py) | Claude Code capture adapter (the only harness-aware code; fail-silent, exits 0 so it can never block a session). |

The committed [`.claude/settings.json`](../../.claude/settings.json) already wires the five Claude Code hook events to the adapter using `$CLAUDE_PROJECT_DIR`, so a fresh clone starts capturing on the next session.

## Usage

```bash
OBS=engineering-projects/legati-observatory/obs.py
python3 $OBS agent writer                                       # on persona switch — attribute events to this legatus
python3 $OBS task "what I'm doing"                              # set current task
python3 $OBS who                                               # who's live
python3 $OBS lock acquire dashboards --task "refresh" --ttl 20  # claim before a risky shared write
python3 $OBS lock release dashboards
python3 $OBS render                                            # markdown dashboard -> render/dashboard-<host>.md
python3 $OBS render --html                                     # interactive HTML  -> render/dashboard-<host>.html
python3 $OBS render --html --since 7d                          # HTML embed window: today|7d|30d|all (default 30d)
```

**Two surfaces, both static + gitignored + per-host:**
- **Markdown** (`render/dashboard-<host>.md`) — the at-a-glance view: live sessions, locks, today's feed/cost, Mermaid orchestration graph.
- **HTML** (`render/dashboard-<host>.html`) — open in a browser (`file://`, no server). Event data is embedded as JSON with vanilla JS, so the **zoom levels are interactive in-page**: time-range (now / today / 7d / 30d / all), filter by agent/project, free-text search, click a session to drill into its full timeline. Cost bars + counts recompute on every control change.

All machine state lives under `<repo>/.observatory/` (hidden) and the rendered dashboards under `render/` — **both gitignored**, because they are machine- and host-dependent.

> The HTML orchestration graph uses Mermaid. To render the graph offline, drop a `mermaid.min.js` into `engineering-projects/legati-observatory/vendor/` (it is gitignored). Without it the HTML still renders — the graph just shows as text, and `obs render --html` prints the hint.

## License

See the repository [`LICENSE`](../../LICENSE).
