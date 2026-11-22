# 7. The scaffold

The workshop repo is a scaffold for a long-running collaboration. Understanding what that means structurally is worth the ten minutes it takes to read this.

## AGENTS.md is the contract

`AGENTS.md` is the first thing any agent reads at session start, under any harness: Codex reads it natively, and Claude Code loads it through the one-line `@AGENTS.md` import at the top of `CLAUDE.md`. It's not documentation — it's operating instructions. It defines, or points to:
- Who the agents are and what their lanes are
- What skills are available and how to invoke them
- What compute tiers exist and when to use them
- What the non-negotiable rules are

When you change a behavior — add an agent, deprecate a skill, change a routing rule — `AGENTS.md` is where the change lives. Not in a memory file, not in a comment in a script. The contract. If the change only concerns one harness, it goes in that harness's appendix (Claude Code's is in `CLAUDE.md`, Codex's at the end of `AGENTS.md`).

## The portability discipline

The workshop scaffold should not depend on any specific AI tool, platform, or provider. The skills are plain markdown files. The memory is plain markdown. The tools are plain Python scripts. The agent identities are plain markdown. None of it requires Claude Code specifically, or any particular version of Claude, or any particular plugin.

This is not an accident. The repo is the durable layer precisely because it's provider-agnostic. When Claude Code adds a new hook system, or changes its command format, or gets replaced by a better tool — the workshop survives. The durable layer is the skills and memories and identities in this repo. The AI is the engine that rotates underneath.

The practical implication: when you're building a new skill or tool, don't tie it to a Claude Code-specific mechanism unless there's no alternative. Natural language invocation ("run the status skill") is more portable than a slash command, which depends on the shell parsing it correctly.

## INDEX.md maintenance — the non-optional rule

Every change to the filesystem — every file added, renamed, moved, or deleted — requires updating `INDEX.md` in the same commit. No exceptions.

This sounds like unnecessary overhead. It's the opposite. The INDEX is what allows any session — any agent, any model, any future tool — to orient in the repo without reading every file. When the INDEX is stale, the repo becomes opaque. Opaque repos accumulate dead code, superseded drafts, and orphaned references that no one wants to clean up because no one knows what's safe to remove.

The discipline is: "done" means the INDEX is updated.

## The archive-not-delete rule

Never delete anything from the workshop. Old drafts, superseded notes, orphaned scripts, failed experiments — they all go to `archive/`, with a brief note about what they were and why they were set aside. The archive is preservation for future mining, not a trash can you have to empty.

The reason is partly practical — you'll want that draft back more often than you think — and partly intellectual. The history of what you tried and abandoned is part of the intellectual record of a project. A year from now you may not remember why you discarded an approach. The archive entry tells you.

## Multiple sessions, same repo

When you're deep in a project, it's common to run multiple sessions simultaneously, under Claude Code, Codex or both — one for writing, one for engineering, one handling background tooling. This is fine, but it requires coordination. The coordination mechanism is the per-project `BACKLOG.md`. Before any session starts work in a project folder, it checks the BACKLOG for what's in flight. Before it commits, it updates the BACKLOG.

The corollary: don't run two sessions that regenerate the same dashboard or shared file simultaneously. Race conditions in a plain-text repo look like "File has been modified since read" errors and partial commits. The BACKLOG convention prevents most of them. Chapter 8 covers the rest: lanes, hand-offs, and the commit discipline that keeps several legati working across machines and harnesses.

## When to add a skill

Add a skill when you find yourself explaining the same multi-step operation to an agent more than twice. If you're writing "read the writing profile, check the domain, use the three-document chain, run a prose-tic sweep before output" in every writing session, that's a skill. Write it once; invoke it forever.

The skill file is not a procedure. It's a briefing — what the operation is, why it matters, and what the agent needs to check before, during, and after. A good skill file is short: under 200 lines. If it's longer, you're documenting edge cases that belong in `memory/` or in the agent's `rules.md`.
