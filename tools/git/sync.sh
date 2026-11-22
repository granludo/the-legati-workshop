#!/usr/bin/env bash
# tools/git/sync.sh: the ONLY git write path for legati sessions, on any machine, under any harness.
#
# Why: several sessions (Claude Code, Codex …) may work on this repo at once, from one machine or
# several. Git is the bus between them. This script makes every session do the same safe thing:
# path-scoped staging (never -A / -a), trailers that say who and where, rebase before push, and push
# right away so the commit is actually visible to the others. See legati/README.md.
# On macOS it lifts the uchg (immutable) flag on files a rebase must rewrite and restores it after.
#
#   sync.sh fetch                        refresh remote refs; report the actual failure
#   sync.sh status                       branch, ahead/behind, dirty files, unread handoffs
#   sync.sh pull [--autostash]           fetch + rebase onto origin (refuses on a dirty tree unless --autostash)
#   sync.sh commit -m MSG|-F FILE [--no-push] -- PATH...   stage PATHs, commit with trailers, rebase, push
#   sync.sh push                         rebase local commits onto origin, push
#   sync.sh log [--since REF|DATE]       commits since this host+harness+legatus last looked (marker updated)
#   sync.sh whoami                       legatus / harness / host as the trailers will record them
#
# Exit codes: 0 ok · 2 rebase conflict (instructions printed) · 3 dirty tree on pull · 4 usage · 5 offline (commit kept locally)
set -uo pipefail
# An external project can use the same discipline without copying the tooling:
#   LEGATUS_REPO="$HOME/Code/other-project" bash tools/git/sync.sh status
REPO="${LEGATUS_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
STATE_TOOL="$(cd "$(dirname "${BASH_SOURCE[0]}")/../legati" && pwd)/state.py"
cd "$REPO" || exit 1

harness() {
  if   [ -n "${LEGATUS_HARNESS:-}" ]; then echo "$LEGATUS_HARNESS"
  elif [ -n "${CLAUDE_CODE_SESSION_ID:-}${CLAUDE_SESSION_ID:-}${CLAUDECODE:-}" ]; then echo claude-code
  elif [ -n "${CODEX_SANDBOX:-}${CODEX_HOME:-}${CODEX_THREAD_ID:-}${CODEX_SANDBOX_NETWORK_DISABLED:-}" ]; then echo codex
  else echo unknown; fi
}
legatus() {
  # Observatory per-session marker (written by `obs.py agent <name>` on a persona switch).
  # A marker under ANY id this session is known by wins (launcher id first, then harness ids), so the
  # name survives when the launcher env is gone but the Codex thread id / Claude session id remains.
  local sid name
  for sid in "${LEGATUS_SESSION:-}" "${CLAUDE_CODE_SESSION_ID:-}" "${CLAUDE_SESSION_ID:-}" "${CODEX_THREAD_ID:-}"; do
    [ -n "$sid" ] || continue
    sid="${sid//\//_}"
    [ -f ".observatory/sessions/$sid.agent" ] || continue
    name="$(tr -d '[:space:]' < ".observatory/sessions/$sid.agent")"
    if [ -n "$name" ]; then echo "$name"; return; fi
  done
  echo "${LEGATUS_AGENT:-unknown}"
}
host() { hostname -s; }
branch() { git symbolic-ref --short -q HEAD; }
fetch() {
  local error rc category
  error="$(git fetch -q origin 2>&1)" && return 0
  rc=$?
  case "$error" in
    *"Operation not permitted"*|*"Read-only file system"*) category="permission failure";;
    *"Authentication failed"*|*"could not read Username"*|*"Permission denied (publickey)"*) category="authentication failure";;
    *"Permission denied"*) category="permission failure";;
    *"Could not resolve"*|*"Could not connect"*|*"Connection timed out"*|*"Network is unreachable"*) category="connectivity failure";;
    *) category="fetch failure";;
  esac
  printf '[sync] %s; remote state not refreshed\n%s\n' "$category" "$error" >&2
  return "$rc"
}
counts() { git rev-list --left-right --count "HEAD...origin/$1" 2>/dev/null || echo "0 0"; }   # "ahead behind"
dirty_n() { git status --porcelain | wc -l | tr -d ' '; }

# macOS: you may keep some tracked files under the immutable flag (uchg, e.g. .claude/settings.json).
# git cannot replace such a file, so a rebase that touches one dies halfway and leaves the tree
# half-updated. Lift the flag on the files the rebase will rewrite, rebase, put it back on success;
# on a conflict leave them unlocked so the resolution can be written.
locked_files() {   # files differing between HEAD and origin/$1 that carry uchg (macOS only)
  [ "$(uname -s)" = Darwin ] || return 0
  git diff --name-only HEAD "origin/$1" 2>/dev/null | while IFS= read -r f; do
    [ -e "$f" ] || continue
    case "$(stat -f '%Sf' "$f" 2>/dev/null)" in *uchg*) printf '%s\n' "$f";; esac
  done
}
rebase_onto() {    # rebase_onto BRANCH [git-rebase args…]  → same exit code as git rebase
  _br="$1"; shift
  _locked="$(locked_files "$_br")"
  if [ -n "$_locked" ]; then
    printf '%s\n' "$_locked" | while IFS= read -r f; do chflags nouchg "$f"; done
    echo "[sync] uchg lifted for the rebase: $(printf '%s' "$_locked" | tr '\n' ' ')"
  fi
  git rebase -q "$@" "origin/$_br"; _rc=$?
  if [ -n "$_locked" ]; then
    if [ $_rc -eq 0 ]; then
      printf '%s\n' "$_locked" | while IFS= read -r f; do [ -e "$f" ] && chflags uchg "$f"; done
    else
      echo "[sync] left UNLOCKED until the rebase is resolved (relock: chflags uchg <file>): $(printf '%s' "$_locked" | tr '\n' ' ')"
    fi
  fi
  return $_rc
}

cmd_whoami() { echo "legatus=$(legatus) harness=$(harness) host=$(host)"; }

cmd_status() {
  BR="$(branch)"; [ -z "$BR" ] && { echo "detached HEAD: refuse to sync"; exit 4; }
  if fetch; then NET=online; else NET=unavailable; fi
  set -- $(counts "$BR"); AH=$1; BE=$2
  echo "[sync] $(cmd_whoami)  branch=$BR  $NET  ahead=$AH behind=$BE  dirty=$(dirty_n)"
  [ "$(dirty_n)" != "0" ] && git status --porcelain | sed 's/^/   /' | head -20
  if [ -f tools/legati/handoff.py ]; then python3 tools/legati/handoff.py inbox --quiet; fi
  return 0
}

cmd_pull() {
  AUTOSTASH=0; [ "${1:-}" = "--autostash" ] && AUTOSTASH=1
  BR="$(branch)"; [ -z "$BR" ] && { echo "detached HEAD: refuse to sync"; exit 4; }
  fetch || { echo "[sync] fetch failed: nothing pulled"; return 5; }
  set -- $(counts "$BR"); BE=$2
  [ "$BE" = "0" ] && { echo "[sync] up to date with origin/$BR"; return 0; }
  if [ "$(dirty_n)" != "0" ] && [ $AUTOSTASH -eq 0 ]; then
    echo "[sync] behind by $BE but the tree is dirty ($(dirty_n) files). Commit first (sync.sh commit …) or pass --autostash."
    echo "       (on a shared tree --autostash stashes OTHER sessions' work in progress too: prefer committing)"
    return 3
  fi
  if rebase_onto "$BR" $([ $AUTOSTASH -eq 1 ] && echo --autostash); then
    echo "[sync] rebased onto origin/$BR (pulled $BE commit(s))"
    return 0
  fi
  conflict_help; return 2
}

conflict_help() {
  echo "[sync] REBASE CONFLICT. Resolve, then continue:"
  echo "       git status                      # files marked 'both modified'"
  echo "       (edit; on shared index files keep BOTH sides' lines)"
  echo "       git add <file> && git rebase --continue"
  echo "       bash tools/git/sync.sh push      # then push"
  echo "       git rebase --abort               # to give up and ask the principal"
}

cmd_push() {
  BR="$(branch)"; [ -z "$BR" ] && { echo "detached HEAD: refuse to sync"; exit 4; }
  case "$(git remote get-url origin 2>/dev/null)" in *github.com[:/]granludo/the-legati-workshop*)
    if [ "${LEGATUS_ALLOW_SCAFFOLD_PUSH:-0}" != 1 ]; then
      echo "[sync] origin is the public scaffold: commit kept locally. Point origin at your own PRIVATE repository first (skills/start-here.md, step 6)."; return 5
    fi;;
  esac
  fetch || { echo "[sync] fetch failed: commit(s) kept locally; run 'sync.sh push' when back on the network"; return 5; }
  set -- $(counts "$BR"); AH=$1; BE=$2
  if [ "$BE" != "0" ]; then
    rebase_onto "$BR" --autostash || { conflict_help; return 2; }
  fi
  # A missing remote branch also yields counts of 0/0; it still needs its first push.
  if [ "$AH" = "0" ] && [ "$BE" = "0" ] && git show-ref --verify --quiet "refs/remotes/origin/$BR"; then
    echo "[sync] nothing to push"; return 0
  fi
  if git push -q origin "HEAD:$BR"; then echo "[sync] pushed $(git rev-parse --short HEAD) → origin/$BR"; return 0; fi
  echo "[sync] push failed (non-fast-forward or auth): run 'sync.sh push' again"; return 5
}

lane_nudge() {   # AGENTS.md §3: warn (never block) when committing into a project where I hold no lane
  local me="$1"; shift; local seen="" p d
  case "$me" in unknown) return 0;; esac
  for p in "$@"; do
    d="${p#$REPO/}"; d="${d#./}"; [ -d "$d" ] || d="$(dirname "$d")"
    while [ -n "$d" ] && [ "$d" != "." ] && [ "$d" != "/" ]; do
      case "$d" in characters|characters/*|memory|memory/*|archive|archive/*|legati/handoffs) break;; esac   # personal / shared, no lanes
      if [ -f "$d/BACKLOG.md" ]; then
        case " $seen " in *" $d "*) ;; *)
          seen="$seen $d"
          grep -qF "[!lane] LANE — $me@" "$d/BACKLOG.md" \
            || echo "[sync] no lane held by $me in $d/: claim one with python3 tools/legati/lane.py claim $d \"<task>\"  (AGENTS.md §3; another session may be in there)";;
        esac
        break
      fi
      d="$(dirname "$d")"
    done
  done
}

cmd_commit() {
  MSG=""; MSGFILE=""; PUSH=1; PATHS=()
  while [ $# -gt 0 ]; do
    case "$1" in
      -m) MSG="$2"; shift 2;;
      -F) MSGFILE="$2"; shift 2;;
      --no-push) PUSH=0; shift;;
      --) shift; PATHS=("$@"); break;;
      *) echo "unknown arg $1"; exit 4;;
    esac
  done
  [ ${#PATHS[@]} -eq 0 ] && { echo "[sync] commit needs explicit paths after --  (never -A, never '.')"; exit 4; }
  for p in "${PATHS[@]}"; do case "$p" in .|-A|--all|-a) echo "[sync] refusing '$p': name the files"; exit 4;; esac; done
  [ -z "$MSG" ] && [ -z "$MSGFILE" ] && { echo "[sync] commit needs -m MSG or -F FILE"; exit 4; }
  TMP="$(mktemp)"; trap 'rm -f "$TMP"' EXIT
  if [ -n "$MSGFILE" ]; then cat "$MSGFILE" > "$TMP"; else printf '%s\n' "$MSG" > "$TMP"; fi
  git interpret-trailers --in-place --if-exists addIfDifferent \
    --trailer "Legatus: $(legatus)" --trailer "Harness: $(harness)" --trailer "Host: $(host)" "$TMP"
  git add -- "${PATHS[@]}" || exit 4
  if git diff --cached --quiet; then echo "[sync] nothing staged from those paths"; exit 0; fi
  git commit -q -F "$TMP" || exit 4
  echo "[sync] committed $(git rev-parse --short HEAD): $(git log -1 --format=%s)"
  case "$(head -1 "$TMP")" in Lane:*) ;; *) lane_nudge "$(legatus)" "${PATHS[@]}";; esac
  [ $PUSH -eq 1 ] && cmd_push
  return $?
}

cmd_log() {
  SINCE=""; [ "${1:-}" = "--since" ] && SINCE="$2"
  MARK="$(python3 "$STATE_TOOL" path "$REPO" "$(harness).$(legatus).last-seen")" || return 1
  if [ -z "$SINCE" ]; then
    if [ -f "$MARK" ] && git cat-file -e "$(cat "$MARK")" 2>/dev/null; then SINCE="$(cat "$MARK")"; else SINCE="--since=24.hours"; fi
  fi
  case "$SINCE" in --since=*) RANGE="$SINCE";; *) RANGE="$SINCE..HEAD";; esac
  # One record per commit, tab-separated, terminated by RS (0x1e): trailer values carry their own
  # newlines, so we strip all newlines and split on RS before formatting.
  git log --no-merges --date=format:'%m-%d %H:%M' \
    --format='%h%x09%ad%x09%(trailers:key=Legatus,valueonly=true,separator=%x2C)%x09%(trailers:key=Harness,valueonly=true,separator=%x2C)%x09%(trailers:key=Host,valueonly=true,separator=%x2C)%x09%s%x1e' $RANGE 2>/dev/null \
    | tr -d '\n' | tr '\036' '\n' \
    | awk -F'\t' '{ who=($3=="" && $4=="" && $5=="") ? "(untagged)" : $3 "/" $4 "@" $5; printf "%s  %s  %-32s %s\n", $1, $2, who, $6 }' \
    | head -40
  git rev-parse HEAD | python3 "$STATE_TOOL" write "$MARK"
}

case "${1:-}" in
  fetch) fetch;;
  status) shift; cmd_status "$@";;
  pull)   shift; cmd_pull "$@";;
  push)   shift; cmd_push "$@";;
  commit) shift; cmd_commit "$@";;
  log)    shift; cmd_log "$@";;
  whoami) cmd_whoami;;
  *) sed -n '2,17p' "$0" | sed 's/^# \{0,1\}//'; exit 4;;
esac
