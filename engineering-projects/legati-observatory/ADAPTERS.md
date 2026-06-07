# ADAPTERS — the portability contract

The Legati Observatory stays portable because **the core (`obs.py` + renderers) knows nothing about any harness.** All harness-specific knowledge lives in `adapters/<harness>/` and its only job is to translate that harness's events into **one schema**. Swap harnesses → write one adapter → done.

## The event schema (the contract)

One JSON object per line, appended to `.observatory/events/<YYYY-MM-DD>.jsonl`. Required: `ts`, `session_id`, `agent`, `host`, `cwd`, `project`, `type`. Optional, when known: `tool`, `target`, `parent_session_id`, `model`, `tokens_in`, `tokens_out`, `cost_usd`.

```json
{"ts":"2026-06-01T18:07:30+02:00","session_id":"abc123","agent":"orchestrator",
 "host":"your-host","cwd":"/path/to/your-workspace","project":"legati-observatory",
 "type":"tool_use","tool":"Edit","target":"obs.py","parent_session_id":null,
 "model":"claude-opus-4-8","tokens_in":0,"tokens_out":0,"cost_usd":0.0}
```

`type` vocabulary: `session_start` · `prompt` · `tool_use` · `tool_result` · `subagent_stop` · `session_end` · `task` · `notification`. An adapter may emit either by importing `obs` and calling `obs.append_event(record)` (used here) or by shelling out to `obs.py emit …`.

**Identity** is resolved by the core from the environment (so it's harness-agnostic):
- `LEGATUS_AGENT` — which legatus (your persona name); default `unknown`.
- `LEGATUS_SESSION` — stable session id; falls back to `CLAUDE_SESSION_ID`, then `host-ppid`.

**Per-persona attribution.** If your workshop switches personas *within* a single session, a static `LEGATUS_AGENT` would mislabel everything. The fix uses the session id the harness exposes to **both** the Bash tool and the hooks (for Claude Code, `CLAUDE_CODE_SESSION_ID`), so an `obs agent <name>` run as a Bash tool and the hook-handler resolve the **same** session. Precedence for `agent`: a per-session marker (`.observatory/sessions/<sid>.agent`, written by `obs agent <name>`) **wins over** the env default. So: set `env.LEGATUS_AGENT` as the session default, and have each persona run `obs agent <name>` on switch — captured tool events then attribute to the active legatus until the next switch. `session_id()` resolves `LEGATUS_SESSION` → `CLAUDE_CODE_SESSION_ID` → `CLAUDE_SESSION_ID` → `host-ppid`.

## Claude Code adapter (the worked example)

`adapters/claude-code/hook-handler.py` reads the CC hook JSON from stdin, maps `hook_event_name` → our `type`, pulls `tool_name` / `tool_input.file_path` → `tool` / `target`, and records via the core. **It exits 0 on every path — it can never block a session.**

Install on a host by adding hooks to that host's **`~/.claude/settings.json`** (or the project `.claude/settings.json`). This repo's committed `.claude/settings.json` already wires them up using `$CLAUDE_PROJECT_DIR`, so a fresh clone captures events out of the box. The manual form:

```jsonc
{
  "hooks": {
    "SessionStart":     [{ "hooks": [{ "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/engineering-projects/legati-observatory/adapters/claude-code/hook-handler.py\"" }] }],
    "PreToolUse":       [{ "matcher": "*", "hooks": [{ "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/engineering-projects/legati-observatory/adapters/claude-code/hook-handler.py\"" }] }],
    "PostToolUse":      [{ "matcher": "*", "hooks": [{ "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/engineering-projects/legati-observatory/adapters/claude-code/hook-handler.py\"" }] }],
    "SubagentStop":     [{ "hooks": [{ "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/engineering-projects/legati-observatory/adapters/claude-code/hook-handler.py\"" }] }],
    "Stop":             [{ "hooks": [{ "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/engineering-projects/legati-observatory/adapters/claude-code/hook-handler.py\"" }] }]
  }
}
```

Verify with `python3 …/obs.py render` and open `engineering-projects/legati-observatory/render/dashboard-<host>.md`.

## How to port to another harness (Codex, …)

1. Copy `adapters/claude-code/` → `adapters/<harness>/`.
2. Rewrite **only** the field mapping in `hook-handler.py`: map that harness's event names → the `type` vocabulary above, and its tool/file fields → `tool`/`target`. Keep the fail-silent, exit-0 discipline.
3. Wire it into that harness's hook/event mechanism (its analogue of `settings.json`).
4. Nothing in `obs.py` or the renderer changes. If the new harness can't emit some fields (cost, tokens), omit them — they're all optional.

That's the whole firewall: harnesses come and go; the schema and the core stay.
