# The Workshop — repository index

**Purpose:** top-level map of the repo. Every folder and root-level file is documented here. Open it when you need to find where something lives (`AGENTS.md` §2).

**Rule:** any change to the filesystem (add, move, rename, delete) requires updating this file in the same commit. Non-optional.

---

## What this repo is

A personal intellectual workspace for long-form writing, research, and thinking with AI legati as collaborators, under Claude Code or Codex (or both), from one machine or several. Multiple writing projects may run in parallel. Each project has its own folder under `writting-projects/` and its own `BACKLOG.md`.

---

## Top-level layout

```
the-workshop/
│
├── AGENTS.md                    # The core: operating instructions every harness reads (Codex natively)
├── CLAUDE.md                    # Claude Code entry point: imports AGENTS.md + a short Claude appendix
├── INDEX.md                     # ← you are here
├── README.md                    # Short pitch + quick start for new users
├── academic-template.typ        # Typst academic PDF template (used by /md2pdf)
├── claude_<name>.sh             # Launch one legatus under Claude Code (generated, one per legatus)
├── codex_<name>.sh              # Launch one legatus under Codex (generated, one per legatus)
│
├── .claude/
│   └── settings.json            # Permissions + hooks (session brief, inbox check, Observatory) for Claude Code
│                                #   (.codex/ is generated per machine by tools/legati/install-hooks.sh codex)
│
├── principals/                  # You — the author
│   └── [your-name]/
│       ├── writing-profile.md   # Your voice (critical for the writer)
│       └── worldview.md         # Your intellectual positions
│
├── characters/                  # Your legati (AI agents)
│   ├── README.md                # How to design them; boot files, roster, launchers, handoff map
│   ├── orchestrator/            # Default legatus (NAME ME): boot.md, character.md, rules.md
│   ├── writer/                  # Writing legatus (NAME ME)
│   ├── comms/                   # Schedule/comms legatus (NAME ME)
│   └── reviewer/                # Reviewer legatus (NAME ME)
│
├── legati/                      # Working together across sessions, machines and harnesses
│   ├── README.md                # The operating manual: sync, lanes, hand-offs, launching, identity
│   ├── roster.toml              # Default harness (claude-code | codex) and model per legatus
│   ├── bin/legatus              # The launcher behind claude_<name>.sh / codex_<name>.sh
│   └── handoffs/                # Messages between legati, one file per message
│
├── memory/                      # Persistent memory across sessions
│   ├── MEMORY.md                # Index (grows over time)
│   ├── reference_hosts.md       # One section per machine, read at boot
│   ├── feedback_*.md            # Starter process rules from the original workshop
│   └── _templates/              # How to write each memory type
│
├── skills/                      # Workshop skills (plain markdown, any harness)
│   ├── README.md                # The skills table: the authority
│   ├── start-here.md            # Onboarding guide — run this first
│   ├── status.md                # Orientation briefing
│   ├── write-as-user.md         # Voice mimicry template (rename for your name)
│   ├── add-source.md            # Source intake pipeline
│   ├── md2pdf.md                # PDF generation (pandoc + Typst)
│   ├── image-gen.md             # Image generation (OpenAI)
│   ├── playwright.md            # Browser automation
│   ├── observatory.md           # Who is live, locks, same-machine chat
│   ├── unslop-text.md           # Strip AI giveaways (EN / CA / ES lists)
│   ├── throat-clearing-review.md # Staged tightening of a release-bound document
│   └── korben-dallas.md         # Short answers on request
│
├── good-practices/              # Guide for new users (written by Marc Alier)
│   ├── INDEX.md
│   ├── 01-the-workshop-idea.md … 07-scaffolding.md
│   └── 08-many-legati-many-harnesses.md
│
├── tools/                       # Working scripts and helpers
│   ├── git/sync.sh              # The only git write path: scoped commits, trailers, rebase, push
│   ├── legati/                  # lane.py, handoff.py, session-start.sh, turn-start.sh, host-section.sh,
│   │                            #   install-hooks.sh, make-launchers.sh, offline tests
│   ├── llm/                     # The `llm` front door for every non-session model call
│   ├── ollama/                  # Ollama wrapper (legacy; kept for tools/wiki)
│   ├── openai/                  # OpenAI API wrapper (images; legacy for text)
│   ├── transcribe/              # Audio transcription (mlx-whisper, Apple Silicon)
│   ├── refs-check/              # Bibliography verification (bibsleuth + URL liveness)
│   ├── wiki/                    # Wiki building tools (embedding-based; a worked example)
│   └── google/                  # Google Workspace setup (for the comms legatus)
│
├── engineering-projects/        # Engineering work (scripts, tools, designs)
│   ├── README.md
│   └── legati-observatory/      # Observability + light coordination; Claude Code and Codex adapters
│
├── sources/                     # Source materials (raw inputs)
│   └── INDEX.md
│
├── writting-projects/           # Active writing projects
│   └── README.md
│
├── archive/                     # Preserved but inactive material (never delete — archive)
│   └── .gitkeep
│
├── TO-PROCESS/                  # Holding folder for raw media awaiting processing
│   └── .gitkeep
│
└── TO-READ/                     # Output folder for reMarkable / PDF outbox
    └── .gitkeep
```

---

## Writing projects

*(none yet — add entries here as projects are created)*

---

## Active agents

*(fill in after running `/start-here`)*

| Name | Role | Boot file | Launch |
|---|---|---|---|
| [Orchestrator] | Default legatus, engineering, coordination | `characters/orchestrator/boot.md` | `./claude_orchestrator.sh` · `./codex_orchestrator.sh` |
| [Writer] | Drafting, editorial, voice mimicry | `characters/writer/boot.md` | `./claude_writer.sh` · `./codex_writer.sh` |
| [Comms] | Schedule, inbox (read-only) | `characters/comms/boot.md` | `./claude_comms.sh` · `./codex_comms.sh` |
| [Reviewer] | Honest feedback on deliverables | `characters/reviewer/boot.md` | `./claude_reviewer.sh` · `./codex_reviewer.sh` |
