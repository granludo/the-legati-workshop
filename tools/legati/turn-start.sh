#!/usr/bin/env bash
# Per-turn check, wired as a UserPromptSubmit hook (Claude Code and Codex). Prints ONLY when there is
# something: unread git handoffs addressed to me, and unread same-machine chat lines (Observatory).
# Never blocks, exits 0. Output is a structured hook envelope, never raw text: both harnesses accept
# hookSpecificOutput/UserPromptSubmit.
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO" || exit 0
out="$(
  python3 tools/legati/handoff.py inbox --quiet 2>/dev/null
  [ -f engineering-projects/legati-observatory/obs.py ] && python3 engineering-projects/legati-observatory/obs.py chat --unread --quiet 2>/dev/null
)"
if [ -n "$out" ]; then
  printf '%s' "$out" | python3 -c 'import json,sys; print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": sys.stdin.read()}}))'
fi
exit 0
