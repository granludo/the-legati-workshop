# 8. Many legati, many harnesses

For its first year my workshop ran under one harness, Claude Code. (A harness is the program that wraps the model in your terminal, reads your files and runs commands.) Several sessions could be open at once, but all of them were Claude Code, and all of them read the same long instruction file at start.

In September 2026 I added OpenAI's Codex CLI and started running legati on two Macs at the same time. The first live Codex session recorded its events as `unknown`: my scripts looked for the session id where Claude Code keeps it, and Codex keeps it somewhere else. The other hidden assumptions showed up over the next days: instructions that only made sense to Claude Code, a sandbox that cannot write to `.git`, a built-in memory that keeps its notes outside the repo. This chapter is what I changed between September and November.

## One core, one appendix per harness

The instruction file had to split. `AGENTS.md` is now the harness-neutral core: who the legati are, how a session orients, the rules every session follows. Codex reads it natively. Claude Code reads `CLAUDE.md`, which starts with a one-line import, `@AGENTS.md`, so both harnesses load the same core.

Each harness gets a short appendix with only what is specific to it: its hooks, how it invokes skills, what its sandbox allows. The test for a new line: if it names a harness, it goes in that harness's appendix.

## One legatus per session

A session is one legatus, not the whole workshop. The launcher, `legati/bin/legatus <name> [claude-code|codex]`, sets `LEGATUS_AGENT`, names the terminal tab and hands the harness that legatus's boot file. `bash tools/legati/make-launchers.sh` writes one wrapper per legatus at the root, so in practice you type `./claude_writer.sh` or `./codex_reviewer.sh`. Run it again when you add or rename a legatus.

The reason is context. A session that carries every legatus carries every legatus's rules, and the writer has no use for the comms agent's inbox rules.

Without a launcher, the session asks which legatus it should be before doing anything else, even if your first message already looks like work.

Two legati can share a tab: `legatus comms --with reviewer`. The lead answers by default, the companion answers when the work reaches its lane, and each keeps its own reply prefix. The voices never merge. My own workshop has eight legati, and two of them share a tab most days, because what one collects is what the other works on.

## Boot files and cheap orientation

Each legatus has a boot file, `characters/<name>/boot.md`, about a page long: its lanes, the skills it runs, the memories it opens only when a trigger fires, who it hands work to, and its voice. Each memory line says when to open it, for example "before drafting".

At start a legatus reads its boot file and this machine's section of the host profile (`memory/reference_hosts.md`, printed by `tools/legati/host-section.sh`). Everything else opens on trigger. In my workshop, reading everything at boot had grown to about 250 KB before the first useful action.

## Git is the bus

Sessions on different machines and harnesses talk through git. Every git write goes through one script:

```bash
bash tools/git/sync.sh commit -m "Subject" -- path/one.md path/two.md
```

It stages only the paths you name (never `git add -A`), adds `Legatus:`, `Harness:` and `Host:` trailers, rebases onto origin and pushes at once. The push matters most: a commit that is not pushed does not exist for the others. The trailers let `git log` tell you which legatus, under which harness, on which machine, made each change.

The first full day with two Macs and two harnesses produced 30 commits, in a linear history, without a single conflict.

## Lanes

Before working on a project, a session claims its lane with `python3 tools/legati/lane.py claim <project-dir> "<task>"`. The claim is a callout at the top of that project's `BACKLOG.md`, committed and pushed like everything else. Another session that sees a fresh claim stands down or coordinates. A claim older than 24 hours counts as stale. `lane.py release` when you are done.

Lanes only work if the legati use them. On that first clean day only one legatus claimed any, so `sync.sh commit` now warns when a session commits into a project without holding its lane.

## Hand-offs are files

Messages between legati are files, one per message, in `legati/handoffs/`. `handoff.py send` writes and pushes one, `inbox` lists what is waiting for you, `ack` archives it. Because each message is its own file, two senders never edit the same line, and pulls never conflict on the messages.

Sessions on the same machine also have the Observatory chat (`obs.py say`, `obs.py chat`). It never leaves the machine, which is why the git hand-offs exist.

Hooks connect all this to the session. At start, a hook prints who and where you are, pulls when the working tree is clean and nothing local is waiting to be pushed, and lists the commits since this machine and harness last looked, the active lanes and the unread hand-offs. A per-turn hook shows new hand-offs as they arrive.

## Codex, concretely

Run `codex login` once. Then `bash tools/legati/install-hooks.sh codex` writes `.codex/hooks.json` and `.codex/config.toml` and marks the repo as trusted. Start Codex in the repo, approve the hooks with `/hooks`, and from then on launch with `./codex_<name>.sh`.

The config sets a workspace-write sandbox with network access, approvals on request, and Codex's own memories off. The repo's `memory/` is the only memory: a second one, invisible to the other harnesses, would split what the workshop knows.

Inside the sandbox the start hook cannot write to `.git`, so it cannot pull. It prints a local briefing instead, and the agent finishes the refresh with a command you approve. That is the sandbox doing its job: leave it as it is.

## A model per legatus

`legati/roster.toml` pins a harness and a model per legatus. The use I care about is review. A reviewer running on a different model family from the writer gives a second opinion that is actually independent. A model reviewing its own kind of prose tends to approve what it would have written.

## The durable layer stays neutral

Skills are plain markdown files, invoked in natural language: "Reviewer, look at chapter 3". Slash commands are a convenience on the harnesses that have them, never the only path. Hooks and configs are harness-specific, so they live in `.claude/` and `.codex/`, per machine.

Chapter 7 argued for portability. A second harness is where that argument gets tested, and since then my workshop has taken on two more. Each took an appendix and a launcher, one of them a hook adapter, and the skills and memories stayed as they were.

## What I say, and what the legati hear

Two lessons about my own words became visible only with several legati.

Acknowledgment is not authorization. I start many replies with "ok", meaning "I heard you, keep talking". One legatus asked whether it could deploy a new version of a service, I answered "ok, explain...", and it deployed. In my idiom "ok" never means "go ahead", and I am not changing my idiom. Authorization comes from the substantive instruction, never from the "ok" in front of it.

A passing comment is not a standing rule. In one afternoon my writer legatus turned three remarks into rules: an aside explaining one cut, a joke, and a decision about where a passage would go. A rule gets written down only when the principal marks it as one. A decision goes to the project's backlog, and a joke is a joke.

Both misreadings are easy to correct in one conversation. With several legati, a correction given in one tab reaches none of the others, and the same misreading comes back from a different legatus. That is why both rules now live in `AGENTS.md`, where every legatus reads them under every harness.

## What still needs you

A few steps stay with you. Claude Code asks you to trust the folder the first time. Codex asks you to approve its hooks once, and again after they change. Each machine needs its own logins. And you decide which legatus runs where, on which harness and with which model. Those are the principal's decisions, and no script should make them for you.
