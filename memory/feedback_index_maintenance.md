---
name: index-maintenance
description: Any change to the filesystem or to project state updates the relevant INDEX.md and BACKLOG.md in the same commit. Starter memory from the original workshop; keep, edit or delete.
metadata:
  type: feedback
---

When files or folders are added, moved, renamed or archived, update the maintained maps **in the same commit**: `INDEX.md` (repo layout and projects), `sources/INDEX.md` (source material), the project's `BACKLOG.md` (what was actually worked on, done or postponed), and `memory/MEMORY.md` when a memory is added.

**Why:** several sessions work on the repo, often in parallel and from different harnesses. Anyone returning after a break, human or legatus, orients from these files. When they drift from the filesystem, every briefing built on them is wrong, and nobody notices until a session acts on a stale map.

**How to apply:**
- Treat the index and backlog update as part of "done", never as a follow-up commit.
- Read the file before adding an entry, so the format stays consistent.
- Finished backlog items move to a done section with the date; they are not deleted (they are the project's history).
- Adding a source: use `/add-source`, which does the index update as part of the pipeline.
- Never bypass this with a "will fix later" commit message.
