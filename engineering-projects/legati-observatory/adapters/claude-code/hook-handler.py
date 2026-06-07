#!/usr/bin/env python3
"""Claude Code -> Legati Observatory capture adapter.

Registered as a hook command in a host's Claude Code settings.json (see
../../ADAPTERS.md). Reads the Claude Code hook JSON from stdin, maps it onto the
Observatory event schema, and records it via the portable `obs` core.

Design contract:
  * This is the ONLY Claude-Code-aware code in the Observatory.
  * It NEVER blocks a session: every failure path exits 0, fast.
  * To port to another harness (Codex, …), copy this file and rewrite only the
    field mapping below so it emits the same schema. The core never changes.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Make the portable core importable (obs.py lives two dirs up).
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
try:
    import obs  # noqa: E402
except Exception:
    sys.exit(0)

# Claude Code hook_event_name -> our event schema "type"
TYPE_MAP = {
    "SessionStart": "session_start",
    "UserPromptSubmit": "prompt",
    "PreToolUse": "tool_use",
    "PostToolUse": "tool_result",
    "SubagentStop": "subagent_stop",
    "Stop": "session_end",
    "Notification": "notification",
}


def main() -> int:
    try:
        raw = sys.stdin.read()
        ev = json.loads(raw) if raw.strip() else {}
    except Exception:
        return 0
    try:
        obs.ensure_dirs()
        # Identity: a per-session env var wins; else fall back to the CC payload.
        if ev.get("session_id") and not os.environ.get("LEGATUS_SESSION"):
            os.environ["LEGATUS_SESSION"] = str(ev["session_id"])
        cwd = ev.get("cwd") or os.getcwd()
        hook = ev.get("hook_event_name", "")
        record = {
            "ts": obs.iso(),
            "session_id": obs.session_id(),
            "agent": obs.agent(),
            "host": obs.host(),
            "cwd": cwd,
            "project": obs.project_of(cwd),
            "type": TYPE_MAP.get(hook, (hook or "event").lower()),
        }
        tool = ev.get("tool_name")
        if tool:
            record["tool"] = tool
            ti = ev.get("tool_input") or {}
            tgt = ti.get("file_path") or ti.get("path") or ti.get("notebook_path")
            if tgt:
                record["target"] = tgt
        if ev.get("parent_session_id"):
            record["parent_session_id"] = ev["parent_session_id"]
        obs.append_event(record)
        obs.touch_presence(cwd=cwd)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
