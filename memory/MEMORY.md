## Repo entry points
- [../INDEX.md](../INDEX.md) — top-level map. Read first after any break.
- [../AGENTS.md](../AGENTS.md) — operating instructions shared by every harness. The core contract.
- [reference_hosts.md](reference_hosts.md) — one section per machine; `bash tools/legati/host-section.sh` prints this machine's.

## Your profile
*(Add pointers here as you write memory files. Example:)*
*(- [Your role and goals](user_role.md) — who you are and what this workshop is for)*

## Feedback
*(Corrections and confirmations that should persist across sessions.)*

Starter memories from the original workshop (process rules that survived many sessions; keep, edit or delete them):
- [Index and backlog maintenance](feedback_index_maintenance.md) — maps and backlogs updated in the same commit as the change.
- [Acknowledgment is not authorization](feedback_ack_is_not_authorization.md) — "ok" means "heard", never "go ahead".
- [A comment is not a rule](feedback_comment_is_not_a_rule.md) — rules only when marked; decisions go to the backlog.
- [Scaffolding portability](feedback_scaffolding_portability.md) — the durable layer stays harness-neutral.
- [Progress updates](feedback_progress_updates.md) — long jobs are never silent.
- [Unpack every reference](feedback_unpack_every_reference.md) — never a bare number, code or path.
- [Push back](feedback_push_back.md) — honest critical feedback, with reasons.

## Projects
*(Active project state — what's in flight, what's next.)*

## References
*(External systems, resources, where to find things.)*
- [Host profiles](reference_hosts.md) — one section per machine, read at boot via `tools/legati/host-section.sh`.

---

> [!todo] You
> This file is an index, not a content store. Each entry is one line pointing to a memory file in this folder. Content lives in the files; the index lives here. Keep it under 200 lines — it's loaded into every session context.
>
> See `memory/_templates/` for how to write each memory type.
> See `good-practices/03-memory.md` for the philosophy behind the memory system.
