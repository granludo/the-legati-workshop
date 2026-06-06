# The Workshop — repository index

**Purpose:** top-level map of the repo. Every folder and root-level file is documented here. Read this at session start.

**Rule:** any change to the filesystem (add, move, rename, delete) requires updating this file in the same commit. Non-optional.

---

## What this repo is

A personal intellectual workspace for long-form writing, research, and thinking with Claude Code as a collaborator. Multiple writing projects may run in parallel. Each project has its own folder under `writting-projects/` and its own `BACKLOG.md`.

---

## Top-level layout

```
the-workshop/
│
├── CLAUDE.md                    # Operating instructions — read at every session start
├── INDEX.md                     # ← you are here
├── README.md                    # Short pitch for new users
├── academic-template.typ        # Typst academic PDF template (used by /md2pdf)
│
├── .claude/
│   └── settings.json            # Pre-approved tool permissions
│
├── principals/                  # You — the author
│   └── [your-name]/
│       ├── writing-profile.md   # Your voice (critical for the Writer agent)
│       └── worldview.md         # Your intellectual positions
│
├── characters/                  # Your legati (AI agents)
│   ├── README.md                # How to design agents
│   ├── orchestrator/            # Default agent (NAME ME)
│   ├── writer/                  # Writing agent (NAME ME)
│   ├── comms/                   # Schedule/comms agent (NAME ME)
│   └── reviewer/                # Reviewer agent (NAME ME)
│
├── memory/                      # Persistent memory across sessions
│   ├── MEMORY.md                # Index (grows over time)
│   └── _templates/              # How to write each memory type
│
├── skills/                      # Workshop skills
│   ├── start-here.md            # Onboarding guide — run this first
│   ├── status.md                # Orientation briefing
│   ├── write-as-user.md         # Voice mimicry template (rename for your name)
│   ├── add-source.md            # Source intake pipeline
│   ├── md2pdf.md                # PDF generation (pandoc + Typst)
│   ├── image-gen.md             # Image generation (OpenAI)
│   └── playwright.md            # Browser automation
│
├── good-practices/              # Guide for new users (written by Marc Alier)
│   ├── INDEX.md
│   ├── 01-the-workshop-idea.md
│   ├── 02-the-legati.md
│   ├── 03-memory.md
│   ├── 04-sources.md
│   ├── 05-writing-workflow.md
│   ├── 06-tooling.md
│   └── 07-scaffolding.md
│
├── tools/                       # Working scripts and helpers
│   ├── ollama/                  # Ollama LLM wrapper (edit SERVERS to configure)
│   ├── openai/                  # OpenAI API wrapper
│   ├── transcribe/              # Audio transcription (mlx-whisper, Apple Silicon)
│   ├── refs-check/              # Bibliography verification (bibsleuth + URL liveness)
│   ├── wiki/                    # Wiki building tools (embedding-based)
│   └── google/                  # Google Workspace setup (for comms agent)
│
├── sources/                     # Source materials (raw inputs)
│   └── INDEX.md
│
├── writting-projects/           # Active writing projects
│   └── README.md
│
├── engineering-projects/        # Engineering work (scripts, tools, designs)
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

| Name | Role | Character file |
|---|---|---|
| [Orchestrator] | Default agent, engineering, coordination | `characters/orchestrator/character.md` |
| [Writer] | Drafting, editorial, voice mimicry | `characters/writer/character.md` |
| [Comms] | Schedule, inbox (read-only) | `characters/comms/character.md` |
| [Reviewer] | Honest feedback on deliverables | `characters/reviewer/character.md` |
