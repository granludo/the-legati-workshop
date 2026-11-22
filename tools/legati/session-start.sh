#!/usr/bin/env bash
# Session-start brief for any legatus session (wired as a SessionStart hook: Claude Code through the
# tracked .claude/settings.json, Codex through install-hooks.sh codex; or run by hand). Prints, never
# blocks, always exits 0:
#   who/where · sync state (auto-pull ONLY if the tree is clean) · commits since this host+harness last looked
#   · active lanes · unread handoffs · persona reminder if no legatus is set.
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if [ "${1:-}" = "--codex-hook" ]; then
  # Codex requires structured SessionStart stdout. Keep the ordinary CLI and Claude hook human-readable.
  bash "$REPO/tools/legati/session-start.sh" --local |
    python3 -c 'import json,sys; print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": sys.stdin.read()}}))'
  exit 0
fi
cd "$REPO" || exit 0
SYNC="bash tools/git/sync.sh"
# Hooks cannot request escalation. Inside the Codex sandbox, defer Git writes to an explicit approved
# tool call. --refresh selects the normal fetch/pull flow; it grants no filesystem permissions.
MODE="${1:-auto}"
case "$MODE" in auto|--local|--refresh) ;; *) echo "usage: session-start.sh [--local|--refresh]" >&2; exit 0;; esac
echo "[legati] $($SYNC whoami)  $(date '+%Y-%m-%d %H:%M %Z')"
BR="$(git symbolic-ref --short -q HEAD)"
ORIGIN="$(git remote get-url origin 2>/dev/null)"
if [ -z "$ORIGIN" ]; then
  echo "[legati] no git remote 'origin': working locally (lanes and handoffs still work on this machine)."
elif case "$ORIGIN" in *github.com[:/]granludo/the-legati-workshop*) true;; *) false;; esac; then
  echo "[legati] origin is the public scaffold, not your workshop: no auto-pull. Point origin at your own PRIVATE repository (skills/start-here.md, step 6)."
elif [ "$MODE" = "--local" ] || { [ "$MODE" = auto ] && [ -n "${CODEX_SANDBOX:-}" ]; }; then
  echo "[legati] local briefing only; Git refresh deferred outside the sandbox."
  echo "[legati] agent next step: run bash tools/legati/session-start.sh --refresh through the harness's approved execution path."
elif $SYNC fetch; then
  set -- $(git rev-list --left-right --count "HEAD...origin/$BR" 2>/dev/null || echo "0 0"); AH=$1; BE=$2
  DIRTY=$(git status --porcelain | wc -l | tr -d ' ')
  if [ "$BE" != "0" ] && [ "$DIRTY" = "0" ] && [ "$AH" = "0" ]; then
    # Only when there is no local commit: then the pull is a fast-forward. A hook never rebases local work.
    $SYNC pull >/dev/null 2>&1 && echo "[legati] pulled $BE commit(s) from origin (tree was clean, nothing local)" || echo "[legati] behind by $BE and the pull failed: run bash tools/git/sync.sh pull"
  elif [ "$BE" != "0" ] && [ "$AH" != "0" ]; then
    echo "[legati] diverged from origin ($AH local, $BE remote commit(s)): run bash tools/git/sync.sh pull when you are ready to rebase"
  elif [ "$BE" != "0" ]; then
    echo "[legati] behind origin by $BE commit(s) but the tree has $DIRTY uncommitted file(s): commit them, then bash tools/git/sync.sh pull"
  fi
  [ "$AH" != "0" ] && echo "[legati] $AH local commit(s) not pushed: bash tools/git/sync.sh push"
else
  echo "[legati] remote state not refreshed; showing local information only. Retry through the approved sync execution path."
fi
echo "[legati] commits since this host/harness last looked:"
$SYNC log | sed 's/^/   /' | head -20
echo "[legati] lanes:"; python3 tools/legati/lane.py list 2>/dev/null | head -12
python3 tools/legati/handoff.py inbox --quiet 2>/dev/null
[ -f engineering-projects/legati-observatory/obs.py ] && python3 engineering-projects/legati-observatory/obs.py chat --unread --quiet 2>/dev/null
case "$($SYNC whoami)" in *legatus=unknown*) echo "[legati] no legatus set: persona protocol (AGENTS.md §1): ask the principal which legatus, then load characters/<name>/boot.md. Launchers: ./claude_<name>.sh, ./codex_<name>.sh";; esac
echo "[legati] discipline: legati/README.md · git writes only via tools/git/sync.sh"
exit 0
