# Legati Observatory — DESIGN

## The one-paragraph picture

Three layers, with a hard portability firewall between them. **Capture adapters** (harness-specific, swappable) translate whatever a harness emits into **our event schema** and append it to a plain **event log**. The event log + two tiny state directories (presence, locks) are the **portable core** — they know nothing about any specific harness. **Static renderers** read that core and emit screenshot-ready artifacts (a markdown dashboard, and an interactive single-file HTML). No server, no database, no cloud. Coordination between agents is **stigmergic**: agents write presence/lock traces and read each other's, with no orchestrator.

## Design decisions

1. **Static, not a server.** Append-only event log → render static artifacts on demand. (Why not a webserver: a running process + port + non-portable code + a cloud-DB trust surface. Liveness, if ever wanted, becomes an *optional* `--watch` front-end, never the core.)
2. **Capture = harness hook adapter + self-report.** A hook adapter for the automatic trail; a small `obs` CLI for the things only the agent knows (current task, locks). `ADAPTERS.md` documents the schema + a worked Claude Code adapter so porting to another harness is mechanical.
3. **Agent-to-agent scope v0 = presence + advisory locks.** Structured handoffs are deferred until there are concrete use cases.
4. **Git policy:** the **entire `.observatory/` is gitignored** — events, presence, locks — *and* so are the rendered dashboards. The state is machine-dependent; tracking a shared `dashboard.md` across hosts would be a merge-conflict generator. The renderer writes **per-host `dashboard-<hostname>.md`**. If a teaching snapshot is ever wanted in git, force-add that one file deliberately.

## The portability firewall (the heart of it)

```
 [ Claude Code ]        [ Codex / future ]         ← harnesses
        │                       │
   adapters/claude-code   adapters/<harness>        ← the ONLY harness-aware code
        │                       │
        └────────► our event schema ◄──────────┘    ← the contract (ADAPTERS.md)
                          │
              .observatory/  (event log + presence + locks)   ← PORTABLE CORE
                          │
                  obs render (static)                          ← renderers
                          │
              render/dashboard-<host>.md / .html               ← artifacts
```

The core CLI (`obs`) and the renderers import **nothing** harness-specific. Swapping harnesses = writing one new adapter that emits the same schema. This is the durable-layer-vs-scaffolding firewall: the scaffolding (a harness's hook config) is disposable; the durable layer (schema + core) never depends on it.

## Event schema (the contract — v0)

One JSON object per line, append-only. Minimal on purpose; extend later.

```json
{
  "ts": "2026-06-01T13:35:00+02:00",
  "session_id": "abc123",
  "agent": "orchestrator",              // legatus name (your persona name|unknown)
  "host": "your-host",
  "cwd": "/path/to/your-workspace",
  "project": "legati-observatory",      // derived from cwd, best-effort
  "type": "tool_use",                   // session_start|tool_use|file_touch|heartbeat|session_end
  "tool": "Edit",                       // when type=tool_use
  "target": "engineering-projects/.../DESIGN.md",  // file path when relevant
  "parent_session_id": null,            // set for subagents → orchestration tree
  "model": "claude-opus-4-8",
  "tokens_in": 0, "tokens_out": 0, "cost_usd": 0.0  // best-effort, when the adapter has them
}
```

`agent` + `parent_session_id` give "who is doing what" and "who is orchestrating whom." `project` + `cost_usd` give per-project cost.

## File layout

```
.observatory/                      # hidden, machine state — gitignored
  events/2026-06-01.jsonl          # append-only event log (per-day file)
  sessions/<session_id>.json       # presence/heartbeat
  sessions/<session_id>.agent      # active-legatus marker (set by `obs agent`)
  locks/<slug>.lock                # advisory claims

engineering-projects/legati-observatory/render/   # visible (Obsidian-friendly), gitignored
  dashboard-<host>.md              # the human-readable dashboard
  history/dashboard-<host>-<ts>.md # timestamped snapshot per render
  # (orchestration graph is an inline Mermaid block inside dashboard-<host>.md)
```

Both `.observatory/` and the visible `render/` are gitignored (machine-dependent, per-host). The dashboard lives OUTSIDE the hidden dir because some editors (e.g. Obsidian) don't show dot-directories.

## Presence

Each live session writes/refreshes `sessions/<session_id>.json`:
```json
{ "agent":"orchestrator","host":"your-host","cwd":"...","started":"...","last_seen":"...","current_task":"scaffolding the observatory" }
```
`last_seen` is bumped on every event (hook) and by `obs heartbeat`. A session with `last_seen` older than `STALE_MINUTES` (default 10) is rendered as **stale/dead**. `current_task` is set by the agent via `obs task "..."` — the human-readable "what am I doing" only the agent knows.

`obs who` → prints the live sessions (who, where, doing what). **This is the awareness primitive** an agent calls before a risky op.

## Advisory locks (the part that kills the race bug)

The failure this fixes: two instances regenerate the same shared file (a dashboard, an index) at once → "file modified since read" → partial writes.

Protocol:
- `obs lock acquire <slug> --task "..." --ttl 15`
  → **atomically** creates `locks/<slug>.lock` (via `O_CREAT|O_EXCL` — atomic exclusive create *is* the mutex; not a check-then-write). Contents: owner session, agent, ts, ttl, task.
  → if the file already exists and is **live** (within ttl), acquire **fails** and returns the current owner.
- `obs lock check <slug>` → live owner or free.
- `obs lock release <slug>` → removes it (only the owner should).
- TTL expiry auto-frees a lock whose owner crashed (no deadlock).

**Honest scope:** the lock is *advisory* — the OS doesn't stop a non-cooperating writer; agents honor it by discipline encoded in your agent guide. But because acquire uses atomic exclusive-create, **two cooperating agents cannot both win the same lock** — that closes the actual race. The discipline rule to encode: *before regenerating any shared file, `obs lock acquire` it; if the acquire fails, surface the live owner and stand down.*

## Renderers — static

`obs render` reads the core and writes `render/dashboard-<host>.md`:
- **Presence table** — who's live, host, cwd/project, current task, last-seen age.
- **Active locks** — slug, owner, task, ttl remaining.
- **Recent activity** — last N events, by session.
- **Cost by project** — table.
- **Orchestration** — parent→child session/subagent graph as an **inline Mermaid flowchart** (live/stale node styling).

Regenerated on demand (and optionally by a git pre-commit hook or a file-watcher). Static markdown/HTML = renders in an editor, drops into a screencast, commits cleanly.

Two render surfaces:
- **Markdown** (`render/dashboard-<host>.md`) — the at-a-glance view: live sessions, locks, today's feed/cost, Mermaid orchestration graph.
- **HTML** (`render/dashboard-<host>.html`, via `--html`) — a self-contained single file: event data embedded as JSON + vanilla JS → **interactive zoom in-browser** (time-range now/today/7d/30d/all, agent/project/search filters, session drill-down, cost bars). Still static, no server, no cloud, no CDN.

Each render also writes a timestamped copy to `render/history/`.

## Build scope

1. `.observatory/` layout + `.gitignore`.
2. `obs` CLI (Python, stdlib only, 3.9+): `emit`, `task`, `heartbeat`, `who`, `agent`, `lock {acquire,check,release}`, `render`.
3. `adapters/claude-code/` hook handler + `ADAPTERS.md` (schema contract + worked CC config + how-to-port).
4. Static renderers → `render/dashboard-<host>.md` (+ `--html`).
5. Discipline rule into your agent guide (lock-before-shared-write).

Post-v1: SVG/PNG cost export, an optional `--watch` live view, structured agent-to-agent handoffs.
