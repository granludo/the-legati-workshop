# 3. The memory system

The memory system is what turns a series of sessions into a continuous collaboration. Without it, every session starts from zero: the agent doesn't know who you are, what you're working on, what corrections you've already given, or what decisions you've already made. With it, the first five minutes of every session can be spent doing actual work instead of re-establishing context.

The key insight is the distinction between a memory file and a note. A note is something you wrote. A memory file is something the agent reads at session start. The discipline of writing memory files is the discipline of asking: "what would a new agent — reading only this repo — need to know to serve me well?"

## The four memory types

**User memories** are about you — your role, your expertise, how you prefer to work, what frustrates you. A good user memory isn't a biography; it's a briefing. "I have twenty years of software engineering experience but this is my first serious engagement with academic writing" is useful. "I like to work in the morning and prefer short responses" is marginally useful. "I am a thoughtful person who values good work" is noise.

**Feedback memories** capture corrections and confirmations. When you say "don't do that" to an agent, that's a feedback memory. When you say "yes, exactly — keep doing that," that's also a feedback memory (people forget to write these down, but they're just as important — if you only save corrections, the agents will grow over-cautious). The rule: lead with the rule, add the reason. A correction without a reason will be misapplied.

**Project memories** track the state of active work — what's in flight, what's decided, what's blocked. These decay fast: a project memory from three months ago may be stale. Always include the date and a note on when the memory is no longer relevant.

**Reference memories** point to external resources — where bugs are tracked, which calendar is authoritative, where to find the normativa for a particular process. These are pointers, not content.

## What not to save

This is where people go wrong. The temptation is to save everything — every conversation, every decision, every piece of context. Don't.

Don't save things you can derive from the code or the git history. If the architecture is visible in the files, you don't need a memory file about it. Don't save debugging solutions or fix recipes — the fix is in the code; the commit message has the context. Don't save ephemeral task details — what you're doing right now belongs in a task tracker, not in memory.

Memory is for things that are non-obvious from the current state of the repo and that a new agent reading the repo would need to serve you well. If a future agent could figure it out by reading the files, it's not a memory.

## The MEMORY.md index

`memory/MEMORY.md` is an index, not a content store. It's loaded into every session context. Keep it under 200 lines — it's not a dashboard, it's a pointer file. Each entry is one line: a link to the memory file and a one-line description specific enough that a future agent can decide whether to open the file.

"User profile" is a bad index entry. "User is a civil engineer with ten years of bridge design experience, new to academic writing" is a good index entry — the agent can decide without opening the file whether this is relevant to the current task.

## The archive-not-delete rule

Old memory files that are no longer accurate don't get deleted. They go to `archive/`. The reasons are practical: first, a discarded memory sometimes turns out to be relevant again. Second, the history of what you believed at different points is itself informative. Third, the archive costs nothing — the agent won't read archived files unless you ask it to.

This rule extends to everything in the workshop. Delete nothing. Archive instead.
