# The Legati — your AI agents

This folder holds the identity files for your workshop's AI agents. Each agent is a *legatus* (plural: *legati*) — a delegate who acts on your authority within a defined lane.

The word matters. The AI industry calls these "agents," which implies autonomous action. But what you want are *delegates*: entities that act on your behalf, within boundaries you set, with judgment you have calibrated. The distinction is epistemological, not cosmetic.

---

## The four starter agents

This workshop seeds four agent roles. They have no names, no personalities, and no characters yet. That's your job. Each folder contains a stub `character.md` and an empty `rules.md`. Fill them in.

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

## The CLAUDE.md pointer

When you've named your agents and written their character files, update `CLAUDE.md` to list them by name in the roster section. The roster in CLAUDE.md is the canonical list of who's active. If an agent isn't listed there, the session doesn't know it exists.
