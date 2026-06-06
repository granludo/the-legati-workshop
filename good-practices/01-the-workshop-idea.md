# 1. The workshop idea

Most people use AI the way they use Google: a question, an answer, next question. The session ends, everything resets. The AI learned nothing about you, and you learned nothing about the AI. It's a vending machine — useful, but not a collaborator.

A workshop is the opposite of that. The session ends and something persists: the memory of what you're working on, the memory of how you think and write, the memory of the decisions you've made and why. The next session starts with context that took real time to build. Over months, the difference compounds.

What I notice — and this is the thing I try to explain to colleagues who ask about it — is not that I'm more productive. I'm not. I produce roughly the same number of papers. What changes is the depth of the work. Problems that used to sit in a drawer for years because I could never get enough traction on them become tractable. The AI doesn't solve them. But it holds the context while I think, asks better questions than I would ask myself, and forces me to articulate positions I had been carrying around vaguely. That's not productivity. That's intellectual leverage.

## What the repo does

The workshop repo is the durable layer. It outlasts any single conversation, any model version, any tool upgrade. The AI that reads it today may be a different model than the one that reads it next year — but the repo remembers what both sessions learned. This is the structural insight: **you are not building a chatbot. You are building a long-running collaborator that accumulates context.**

The repo holds:
- The memory system — what the agents know about you, your work, and your preferences
- The skill definitions — what operations the agents can perform
- The tooling — actual working scripts for PDF generation, transcription, source processing, bibliography verification
- The agent identities — the characters you've given to each specialized role

None of this exists in the AI's weights. It's all here, in plain text, under version control. When the AI reads it at session start, it becomes the agent you designed — not a generic assistant.

## The difference this makes

The writing profile is the most concrete example. After running this workshop for a year, I have a document that describes how I write: my rhythm, the phrases I avoid, how I structure arguments, the metaphors I reach for, the register shifts between academic papers and public essays. When I start a session with "load the writing profile," the output stops sounding like AI and starts sounding like me. Not perfectly — the calibration never ends. But the first draft is now usable rather than a demolition project.

That document didn't exist when I started. I built it by noticing when drafts missed, articulating why, and writing the rule. Same with the worldview document — the accumulated intellectual positions that prevent the agents from writing things I'd never say. Same with the memory files that record what happened in past sessions. The system gets better because you invest in it.

## The minimum viable investment

You don't need any of this to be perfect on day one. The scaffold ships with templates and stubs. What you need to do in the first month:

1. Write a first draft of your writing profile. It will be thin. That's fine — it grows.
2. Name your agents and give them at least a one-sentence mission. That's enough to start.
3. Run a few sessions and notice what goes wrong. Write those corrections into `memory/` as feedback files.

The system becomes useful faster than you think. The first time an agent applies a correction from three weeks ago without you having to say it again, you understand why this is worth the setup.

## What it doesn't do

A workshop doesn't make you faster. It doesn't automate your thinking. The agents do not make decisions — you do. They hold context, generate drafts, verify references, surface patterns. The judgment is always yours.

This is a feature, not a limitation. The goal is deep work, not delegated work. An agent that made decisions for you would be replacing your intellectual output with its own. What you want is an agent that prepares the ground so your intellectual output can go deeper.
