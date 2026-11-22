# skills/ — the folder convention and the table

When the principal invokes a skill (by addressing a legatus in natural language, "Writer, unslop chapter 3"; by naming it in passing, "use /add-source on this URL"; or by typing `/<name> <args>`), **read `skills/<name>.md` from this repo and follow the instructions it contains.** This folder is the source of truth for every workshop skill, under every harness.

**Natural-language invocation is canonical.** A bare slash command may be intercepted by the harness's own parser before the legatus sees it; in that case just address the legatus. Skill files are plain markdown, not harness slash commands, so they work the same in Claude Code and in Codex ([memory/feedback_scaffolding_portability.md](../memory/feedback_scaffolding_portability.md)).

**This table is the authority**; each legatus's `boot.md` lists the subset it runs. Adding a skill = the file + a row here. A name without a file → say so, do not guess.

| Invoke | File | Who runs it | What it does |
|---|---|---|---|
| `/start-here` | [start-here.md](start-here.md) | orchestrator | Onboarding: name your legati, write your profile, set up both harnesses and your first project. |
| `/status` | [status.md](status.md) | orchestrator | Read-only orientation briefing: active projects, lanes, handoffs, top backlog items, skills, open decisions. |
| `/write-as-[you]` | [write-as-user.md](write-as-user.md) | writer | Load your writing profile and worldview before any writing task. Rename it after setup. |
| `/add-source` | [add-source.md](add-source.md) | orchestrator (pipeline), writer (analysis) | Intake a source (YouTube, PDF, audio, web article, text) into `sources/`. |
| `/md2pdf` | [md2pdf.md](md2pdf.md) | any | Render markdown to print-ready PDFs via pandoc + Typst. |
| `/image-gen` | [image-gen.md](image-gen.md) | orchestrator | Generate a designed image through an image API. Paid: be deliberate. |
| `/playwright` | [playwright.md](playwright.md) | any | Get a real browser for JS-rendered or login-gated pages: a reusable script under `tools/<slug>/`. |
| `/observatory` | [observatory.md](observatory.md) | any | Who is live, what each session is doing, advisory file locks, same-machine chat. |
| `/unslop-text` | [unslop-text.md](unslop-text.md) | writer (any legatus on its own output) | Strip AI giveaways from a text: per-language blacklists (English, Catalan, Spanish), an adverb audit, formulaic constructions, mannered prose. Subtractive only. |
| `/throat-clearing-review` | [throat-clearing-review.md](throat-clearing-review.md) | writer reports, reviewer grades | Staged tightening of a release-bound document in four passes: phrasing, redundant paragraphs, tables and figures, phrase-level padding. Report first, edit nothing until the principal rules. |
| `/korben-dallas` | [korben-dallas.md](korben-dallas.md) | any, only on request | Compress the answer, not the work: verdict first, two short paragraphs at most. Chat only; files stay full size. |

> [!todo] You
> As you add legati with their own skills (a comms refresh, a reviewer checklist for your field), add rows here and list the skill in that legatus's `boot.md`.
