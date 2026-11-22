---
name: scaffolding-portability
description: Keep the durable layer (skills/, memory/, characters/, project folders, runbooks) harness-neutral. Natural-language invocation is canonical; harness-specific files live in .claude/ and .codex/, per machine. Starter memory from the original workshop; keep, edit or delete.
metadata:
  type: feedback
---

The repo is the durable agent: the model rotates underneath it, and so does the harness (Claude Code today, Codex next to it, something else later). The durable layer must work under any of them without rework.

**Why:** the original workshop started on one harness and later added a second. Every place where a skill or a rule assumed one harness's mechanics had to be found and rewritten. The places that were plain markdown and plain scripts needed nothing.

**How to apply:**
- **Natural-language invocation is canonical** ("Reviewer, look at chapter 3"). A slash command is a typing convenience that depends on one harness's parser.
- **Skills are plain markdown** in `skills/`: no harness-specific frontmatter or placeholders in the body. A file in `.claude/commands/` may exist only as a one-line pointer to the skill.
- **Harness-specific files stay out of the durable layer:** hook wiring, MCP configs, harness settings live in `.claude/` and `.codex/`. What is per machine is gitignored (`.codex/`, `.claude/settings.local.json`).
- **Rules live in `AGENTS.md`**, read by every harness; each harness gets a short appendix with only what is specific to it.
- **Tools are CLIs or scripts** that any harness can call from a shell, never a protocol only one harness speaks.
