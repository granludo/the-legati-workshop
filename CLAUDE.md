# The Legati Workshop: Claude Code entry point

@AGENTS.md

## Claude Code appendix (only what is specific to this harness)

- **If the import above did not load, read [AGENTS.md](AGENTS.md) now.** It is the core; its §1 (become one legatus) comes first.
- **Launch as a legatus with a named tab:** `./claude_<name>.sh` from the repo root. It wraps `legati/bin/legatus <name> claude-code`, which sets `LEGATUS_AGENT`, appends `characters/<name>/boot.md` to the system prompt and names the tab. By hand: `LEGATUS_AGENT=writer claude -n writer --append-system-prompt "$(cat characters/writer/boot.md)"`.
- **Hooks** are in the tracked `.claude/settings.json`, with `$CLAUDE_PROJECT_DIR` paths, so a fresh clone works: the session-start brief, the per-turn inbox check and the Observatory capture. Claude Code asks you to trust the folder the first time. Per-machine additions go in `.claude/settings.local.json` (gitignored).
- **Permissions:** the tracked `.claude/settings.json` carries the `allow` / `deny` rules; deny rules hold in every permission mode. Plain `git push` is denied on purpose: pushes happen inside `tools/git/sync.sh`, after the rebase.
- **Memory:** the repo's `memory/` is the workshop memory, indexed in `memory/MEMORY.md`. Claude Code's own auto-memory (`~/.claude/projects/<repo-slug>/memory/`) is per machine and invisible to Codex and to your other machines: anything worth keeping that lands there moves into `memory/`, with an index line, in the same session.
- **Commits:** put the harness's attribution trailers in the `-m` / `-F` message; `tools/git/sync.sh` adds `Legatus:` / `Harness:` / `Host:`.
- **Slash commands:** `skills/<name>.md` is the only copy of a skill. A file in `~/.claude/commands/` or `.claude/commands/` exists only for typing convenience and is a one-line pointer to the repo skill, never a copy: a copy drifts, and Codex never sees it.
