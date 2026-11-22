# legati/ — working together across sessions, machines and harnesses

Several legati sessions may work on this repo at the same time: two terminal tabs on one machine, a laptop and a desktop, Claude Code next to Codex. Nothing here assumes one harness. The background and the lessons are in [good-practices/08-many-legati-many-harnesses.md](../good-practices/08-many-legati-many-harnesses.md); this file is the operating manual.

## The idea in one paragraph

**Git is the bus.** Every commit is a timestamped, attributed event that any session reads after a pull; hand-offs are files carried by commits; a lane claim is a commit to the project's backlog. Different machines have separate working trees; terminals on one machine may share one checkout. Same-machine sessions additionally get the Legati Observatory's live presence, locks and chat (`engineering-projects/legati-observatory/`); those never cross machines and nothing here depends on them.

## The four rules

1. **All git writes go through `tools/git/sync.sh`.** Path-scoped staging only (never `-A`, never `.`), trailers `Legatus:` / `Harness:` / `Host:` added automatically, rebase onto origin, push at once. A commit that is not pushed does not exist for the others. On macOS the rebase lifts the immutable flag (`uchg`) on files it must rewrite and restores it afterwards.
   ```bash
   bash tools/git/sync.sh commit -m "Subject line" -- path/one.md path/two.md
   bash tools/git/sync.sh status | pull | push | log | whoami
   ```
2. **Claim a lane before working on a project.** `python3 tools/legati/lane.py claim <project-dir> "<task>"` puts a `> [!lane]` callout at the top of that project's `BACKLOG.md` and pushes it. `lane.py list` shows every active lane; a claim younger than 24 hours by someone else means stand down or coordinate. `lane.py release <project-dir>` when done.
3. **Messages are files, one per message.** `python3 tools/legati/handoff.py send --to writer --subject "…" --body "…"` writes `legati/handoffs/<timestamp>_<from>_to_<to>_<slug>.md` and pushes it. Recipients see it with `handoff.py inbox` and archive it with `handoff.py ack <file>` (moved to `legati/handoffs/archive/YYYY-MM/`, committed). `--to all` broadcasts; readers bump a local marker instead of archiving. One file per message is what keeps two senders from ever conflicting on the same line.
4. **Session start = look before you touch.** `bash tools/legati/host-section.sh` prints this machine's section of `memory/reference_hosts.md`. `tools/legati/session-start.sh` fetches, pulls only when the tree is clean and there is no local commit, and lists the commits since this machine and harness last looked, the active lanes and unread hand-offs. `tools/legati/turn-start.sh` surfaces new hand-offs before each prompt. Both are hooked in Claude Code (tracked `.claude/settings.json`) and in Codex (`install-hooks.sh codex`).

## Launching a legatus

| | Claude Code | Codex |
|---|---|---|
| One legatus in this tab | `./claude_<name>.sh` | `./codex_<name>.sh` |
| What it runs | `legati/bin/legatus <name> claude-code` | `legati/bin/legatus <name> codex` |
| How the boot file arrives | appended to the system prompt | Codex reads `AGENTS.md` natively; the opening prompt names the boot file |
| One-time setup per machine | trust the folder when asked | `codex login`, `bash tools/legati/install-hooks.sh codex`, approve `/hooks` once |

- The launcher sets `LEGATUS_AGENT` and `LEGATUS_HARNESS`, names the terminal tab, and starts the harness in the repo root. For Codex it also sets a unique `LEGATUS_SESSION`, so two simultaneous Codex tabs never share an identity.
- **Two legati in one tab:** `legati/bin/legatus comms --with reviewer` (or `comms+reviewer`). `LEGATUS_COMPANIONS` is exported, the tab is titled `COMMS+REVIEWER`, and both boot files are loaded behind a pairing note: the lead answers by default, the companion in its lane, each with its own prefix.
- **Default harness and model per legatus:** `legati/roster.toml`. The root wrappers name the harness explicitly; `legati/bin/legatus <name>` alone uses the roster.
- **New or renamed legatus:** `bash tools/legati/make-launchers.sh` regenerates the wrappers from `characters/*/boot.md`.
- **Dry run:** `LEGATUS_DRY_RUN=1 ./codex_writer.sh` prints the command without launching.
- Extra arguments go to the harness: `./codex_reviewer.sh -m <model>`, `./claude_writer.sh --model <model>`.

## Identity

`Legatus` comes from the Observatory's per-session marker (`obs.py agent <name>` writes it on a persona switch), else from `LEGATUS_AGENT` (the launcher default), else `unknown`. `Harness` is detected from the environment (`LEGATUS_HARNESS` overrides). `Host` is the short hostname.

Session ids resolve in this order: `LEGATUS_SESSION`, `CLAUDE_CODE_SESSION_ID`, `CLAUDE_SESSION_ID`, `CODEX_THREAD_ID`. The Observatory, the git trailers and the hand-offs use the same marker for that id, so a persona switch inside a session is attributed correctly everywhere. A plain `codex` or `claude` start (no launcher) asks which legatus; after the answer, `obs.py agent <name>` pins it.

Offline checks (no harness, no model, no network, no git writes): `python3 -B tools/legati/test_identity.py` and `python3 -B tools/legati/test_state.py`.

## What lives where

| | in git (crosses machines) | per machine (never committed) |
|---|---|---|
| Commits with trailers | ✓ | |
| `legati/handoffs/*.md` and `archive/` | ✓ | |
| Lane callouts in `BACKLOG.md` files | ✓ | |
| "Since last looked", inbox and chat read markers | | `.legati-state/` |
| Observatory events, presence, locks, chat | | `.observatory/` |
| Codex hook wiring and project config | | `.codex/` |
| Claude Code per-machine additions | | `.claude/settings.local.json` |

## When a pull conflicts

It will, occasionally, on shared index files (`MEMORY.md`, `INDEX.md`, a `BACKLOG.md`). Resolution rule: **keep both sides' lines**, then `git add <file> && git rebase --continue && bash tools/git/sync.sh push`. Lanes keep this rare. If in doubt, `git rebase --abort` and ask the principal.

## Your remote

The workshop needs a **private** remote of your own for any of this to cross machines. A fresh clone of the public scaffold still points at it: the session start then skips the pull and `sync.sh push` refuses, until you point `origin` at your own repository (`skills/start-here.md`, step 6).

## Codex inside its sandbox

Codex runs shell commands in a sandbox that may not write `.git` from a hook. The start hook then prints a local briefing and says "Git refresh deferred"; the legatus completes it with `bash tools/legati/session-start.sh --refresh` through Codex's approval flow (the `AGENTS.md` Codex appendix says how). `--local` forces the local briefing in any harness. The generated `.codex/config.toml` keeps `workspace-write` with network and `on-request` approvals; do not widen it.
