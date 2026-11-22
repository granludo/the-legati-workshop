#!/usr/bin/env python3
"""Codex CLI -> Legati Observatory capture adapter.

Registered as a command hook in <repo>/.codex/hooks.json (written by tools/legati/install-hooks.sh codex;
project hooks run only after the repo is trusted in ~/.codex/config.toml and each hook is approved once by
hash via /hooks). Codex's hooks send the same shape Claude Code's do: JSON on stdin with session_id,
hook_event_name, tool_name, tool_input, cwd, turn_id. Only the field mapping below is Codex-aware.

Contract (ADAPTERS.md): never block, exit 0 on every path, emit the shared schema. Adds the optional
`harness` field ("codex").
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
try:
    import obs  # noqa: E402
except Exception:
    sys.exit(0)

TYPE_MAP = {
    "SessionStart": "session_start",
    "SessionEnd": "session_end",
    "UserPromptSubmit": "prompt",
    "PreToolUse": "tool_use",
    "PostToolUse": "tool_result",
    "PermissionRequest": "notification",
    "SubagentStart": "task",
    "SubagentStop": "subagent_stop",
    "Stop": "session_end",
    "Interrupt": "notification",
    "PreCompact": "notification",
    "PostCompact": "notification",
}

PATCH_FILE = re.compile(r"^\*\*\* (?:Update|Add|Delete) File: (.+)$", re.M)


def target_of(tool: str, ti) -> str | None:
    """Best-effort file/command target from Codex tool_input shapes."""
    if not isinstance(ti, dict):
        return None
    if tool in ("apply_patch",) or "patch" in ti:
        m = PATCH_FILE.findall(str(ti.get("patch") or ti.get("input") or ""))
        return ",".join(m[:5]) if m else None
    for k in ("file_path", "path", "filePath", "notebook_path"):
        if ti.get(k):
            return str(ti[k])
    if ti.get("command"):
        c = ti["command"]
        c = " ".join(c) if isinstance(c, list) else str(c)
        return c[:200]
    if ti.get("url"):
        return str(ti["url"])[:200]
    return None


def main() -> int:
    try:
        raw = sys.stdin.read()
        ev = json.loads(raw) if raw.strip() else {}
    except Exception:
        return 0
    try:
        obs.ensure_dirs()
        if ev.get("session_id") and not os.environ.get("LEGATUS_SESSION"):
            os.environ["LEGATUS_SESSION"] = str(ev["session_id"])
        cwd = ev.get("cwd") or os.getcwd()
        hook = ev.get("hook_event_name", "")
        tool = ev.get("tool_name")
        record = {
            "ts": obs.iso(),
            "session_id": obs.session_id(),
            "agent": obs.agent(),
            "host": obs.host(),
            "cwd": cwd,
            "project": obs.project_of(cwd),
            "type": TYPE_MAP.get(hook, (hook or "event").lower()),
            "harness": "codex",
        }
        if tool:
            record["tool"] = tool
            t = target_of(tool, ev.get("tool_input"))
            if t:
                record["target"] = t
        if ev.get("turn_id"):
            record["turn_id"] = str(ev["turn_id"])
        # The harness id outlives the launcher env (Codex: same thread id after a move to the desktop app);
        # pin the resolved legatus under it so later hooks and shells still know who this is.
        if ev.get("session_id"):
            obs.remember_agent(str(ev["session_id"]), record["agent"])
        obs.append_event(record)
        obs.touch_presence(cwd=cwd)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
