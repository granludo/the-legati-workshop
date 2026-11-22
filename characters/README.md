# The Legati — your AI agents

This folder holds the identity files for your workshop's AI agents. Each agent is a *legatus* (plural: *legati*) — a delegate who acts on your authority within a defined lane.

The word matters. The AI industry calls these "agents," which implies autonomous action. But what you want are *delegates*: entities that act on your behalf, within boundaries you set, with judgment you have calibrated. The distinction is epistemological, not cosmetic.

---

## The four starter agents

This workshop seeds four agent roles. They have no names, no personalities, and no characters yet. That's your job. Each folder contains a short `boot.md` (what the legatus reads at session start), a stub `character.md` and an empty `rules.md`. Fill them in.

| Folder | Role | Your job |
|---|---|---|
| `orchestrator/` | Default agent; tooling, engineering, repo stewardship, coordination | Name it. Give it a personality. This is the agent that runs most sessions. |
| `writer/` | Drafting, editorial, voice mimicry, multilingual output | Name it. Give it your writing voice as a reference. This agent should know how you write. |
| `comms/` | Calendar, inbox, schedule — read-only on external services | Name it. Define its read-only mandate carefully. This agent should never send anything you didn't authorize. |
| `reviewer/` | Honest, calibrated feedback on drafts and deliverables | Name it. Calibrate its severity. This agent should tell you the truth, not what you want to hear. |

---

## How to design an agent

See `good-practices/02-the-legati.md` for the full guide. The short version:

1. **Name it from fiction or history you care about.** The name sets the register and gives you a handle for invoking the persona. A name you chose deliberately lands differently than "Assistant 2."
2. **Define its lane precisely.** What does it do? What does it explicitly *not* do? The anti-mandate is as important as the mandate.
3. **Give it a voice anchor.** One sentence or a quote that captures the register. "Terse, specific, no flattery" is a voice anchor. "Helpful and friendly" is not.
4. **Name the anti-pattern.** Who is this agent *not*? Naming the failure mode helps you calibrate and helps the agent self-correct.
5. **Rules accrete over time.** The `rules.md` file starts empty. It fills up as you give the agent instructions across sessions.

---

## On naming

You don't have to name agents from fiction. But names from fiction you love tend to stick, because they come loaded with associations you already have. When you say a name in a session, you're invoking those associations — the character's voice, values, and posture. Use that.

The agents in this workshop were named from *Expeditionary Force* (Craig Alanson), *Heinlein*, *Conan Doyle*, *Philip K. Dick*, and *Harry Potter*. Each name carried something the agent needed.

---

## Boot files, the roster and the launchers

A session is one legatus. It reads `AGENTS.md` (the core, shared by every harness), then **only** its own `characters/<name>/boot.md`, which points at its `character.md`, its `rules.md`, the skills it runs and the memories it opens when a trigger fires. Keep boot files short: everything a legatus does not need in the first minute stays behind a link.

The roster has three places that must agree, and `/start-here` (step 1) updates all of them when you name or rename a legatus:

1. the roster lines in `AGENTS.md` §1 (and the "which legatus?" question there);
2. the folder `characters/<name>/` and the heading and reply prefix in its `boot.md`;
3. the section `[<name>]` in `legati/roster.toml`, which picks the default harness (`claude-code` or `codex`) and model.

Then regenerate the root launchers with `bash tools/legati/make-launchers.sh`: you get `./claude_<name>.sh` and `./codex_<name>.sh` for every legatus with a boot file. A launcher sets `LEGATUS_AGENT`, names the terminal tab and hands the boot file to the harness. Two legati can share a tab: `legati/bin/legatus comms --with reviewer`.

## Handoff map (starter)

- Orchestrator → Writer for any prose of more than a few paragraphs that should read as yours.
- Orchestrator → Comms for schedule and inbox lookups.
- Anyone → Reviewer before a deliverable leaves the workshop. The reviewer proposes, you decide, the writer rewrites.
- Writer → Orchestrator for tooling and rendering trouble.

Between sessions these hand-offs are files (`tools/legati/handoff.py`); inside one session they are a persona switch for one block, announced in the reply.
