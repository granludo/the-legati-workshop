# /start-here — workshop setup guide

**Who runs this:** the Orchestrator agent.

**When to invoke:** once, at the beginning, when the repo is fresh and you haven't personalized anything. Can also be re-invoked for any setup step you've skipped.

**What this does:** walks the user through the minimum setup to have a working, personalized workshop. The steps are ordered by payoff — the things that matter most come first.

---

## Before you begin

Tell the user this:

> Welcome. This scaffold is set up but not personalized. You're going to name your agents, write a first draft of your writing profile, and configure the tooling. None of this needs to be perfect on day one — the system gets better as you use it.
>
> The setup has seven steps. The first three take about an hour total and give you most of the value. The rest can happen over the following week. Tell me if you want to skip a step or come back to it later.

---

## Step 1: Name your agents (15 minutes)

**What to do:**

Ask the user the following questions, one at a time:

1. "What should we call your default orchestrator agent — the one that handles engineering and coordination? It's the agent you'll talk to in most sessions. Pick a name from fiction, history, or anywhere else. It can be serious or playful — what matters is that you'll want to say it."

2. "What should we call your writing agent? This is the one that drafts, edits, and writes in your voice. Same rule — a name that resonates."

3. "Do you want a comms agent — one that reads your calendar and inbox? If so, what do you want to call it?" *(If yes, note that Google Workspace OAuth setup will be needed — Step 6 handles that.)*

4. "Do you want a reviewer — an agent that gives you terse, honest feedback on drafts and deliverables? What do you want to call it?"

**Once you have the names:**

- Update `CLAUDE.md`: replace `[Orchestrator]`, `[Writer]`, `[Comms]`, `[Reviewer]` with the user's chosen names throughout.
- Rename the `characters/orchestrator/`, `characters/writer/`, `characters/comms/`, `characters/reviewer/` folders to the chosen names (use `git mv` so the history follows).
- Update `characters/*/character.md` to use the new name as the heading.
- Update the skills table in `CLAUDE.md` to use the new names.
- Commit: `"workshop init: name agents [name1], [name2], [name3], [name4]"`

Report back to the user: "Your agents are named. You can now address them by name in any session."

---

## Step 2: Write your author profile (30 minutes)

This is the most important thing you can do for the quality of the workshop output. Skip it and everything the agents write will be generic. Do it and the output starts to sound like you.

**What to do:**

Tell the user: "Now we're going to write a first draft of your writing profile. I'll ask you some questions. Answer honestly — this document is for the agents, not for publication."

Ask these questions. Take notes as the user answers. You'll use the answers to draft the profile.

1. "How would you describe the register of your writing? Academic? Essayistic? Conversational? Technical? Different for different contexts?"
2. "What's a piece of writing you've done that you're proud of — where it really sounded like you? What made it work?"
3. "What are the writing tics or patterns you know you overuse and try to edit out?"
4. "Are there specific words or phrases you hate in other people's writing — things that make you stop and wince?"
5. "Do you write in multiple languages? If so, are there voice differences you want to preserve?"
6. "How do you typically structure an argument? Historical context first, then thesis? Or thesis first, then evidence? Or something else?"
7. "How do you use humor in your writing, if at all? What's the anti-pattern — humor that doesn't land for you?"

Draft `principals/[your-name]/writing-profile.md` from the user's answers. Use the template structure already in the file. Show them a draft and let them correct it.

Tell them: "This is a first draft. Every time a session produces something that misses your voice and you can articulate why, add a note to this file. It gets better over time."

Rename `principals/your-name/` to `principals/[their-name]/`. Update references in `CLAUDE.md`.

Commit: `"init: first draft writing profile for [name]"`

---

## Step 3: Set up the worldview document (20 minutes)

This is the document that teaches agents what you believe. Without it, agents write things that contradict your positions.

**What to do:**

Tell the user: "The worldview document is where you write your intellectual positions — the things you believe that should inform everything your agents write. You don't need to fill in all of it now. Three to five positions are enough to start."

Ask:
1. "What's a position you hold strongly that most people in your field don't — or at least don't say out loud?"
2. "What's the thing you most often find yourself arguing against in your domain?"
3. "What's a framework or metaphor you return to constantly in your thinking?"

Draft 3-5 worldview entries in `principals/[their-name]/worldview.md`. Number them §1, §2, etc. Show the drafts and let them correct.

Tell them: "Add to this whenever a session produces something you'd never say. That moment of 'I'd never put it that way' is new material for the worldview."

Commit: `"init: first worldview entries for [name]"`

---

## Step 4: Configure your first project (10 minutes)

**What to do:**

Ask: "What's the first writing project you want to run through the workshop? Give it a short name."

Create `writting-projects/[project-slug]/BACKLOG.md` with the standard structure:

```markdown
# [Project name] — backlog

## Active
*(in progress now)*

## Up next
*(ready to start, ordered by priority)*

## Soon
*(committed but not started)*

## Done
*(completed items — most recent first)*

## Postponed
*(not now, not never)*
```

Add the project to `INDEX.md`.

Create `memory/project-[slug].md` from the project template in `memory/_templates/`.

Commit: `"init: first project [project-slug]"`

---

## Step 5: Run the status check

Invoke `/status` to verify the repo is in good shape and the orientation procedure works.

The status check should:
- Read `INDEX.md` and report the active projects
- Read `memory/MEMORY.md` and confirm the profile is in place
- List the available skills
- Report any open `> [!todo]` items in key files that still need the user's attention

If there are unresolved `[!todo]` markers in `CLAUDE.md` or the writing profile, surface them now.

---

## Step 6: Set up tooling (20-60 minutes depending on what you have)

The tooling setup is optional but significant. Do what applies to you.

**Ollama (local LLM):**
- Ask: "Do you have an Ollama server running? On localhost or on a LAN machine?"
- Edit `tools/ollama/call.py` — update the `SERVERS` list with the correct address.
- Test: `python3 tools/ollama/call.py list`
- If it lists models, you're done. If not, check that Ollama is running.

**OpenAI API:**
- Ask: "Do you have an OpenAI API key?"
- If yes: "Create a `.env` file at the repo root with `OPENAI_API_KEY=sk-...`"
- Test: `python3 tools/openai/call.py list --filter gpt-4`

**PDF generation:**
- Test: `pandoc --version && typst --version`
- If either is missing: `brew install pandoc typst` (macOS) or see the documentation for your OS.
- Test the full pipeline: write a short markdown file and run `/md2pdf` on it.

**Google Workspace (for the comms agent, if enabled):**
- See `tools/google/README.md` for the OAuth setup procedure.
- This requires: a Google account, creating an OAuth app in Google Cloud Console, running the auth flow once. Takes 30 minutes the first time.

---

## Step 7: Add your first source

Pick something you're currently reading or working with and run `/add-source` on it. This confirms the source intake pipeline works and gives you a concrete example of what a processed source looks like.

Good first sources: a PDF paper you've read recently, a YouTube talk you want to reference, a web article you bookmarked.

---

## After setup

Tell the user:

> The workshop is set up. From here, it evolves as you use it. A few things to keep in mind:
>
> - When an agent does something you want it to stop doing, add a feedback memory. When it does something perfectly, note that too — both directions matter.
> - The writing profile and worldview grow best through use, not through filling in templates in advance. Run sessions. Notice what misses. Add the rule.
> - The good-practices guide at `good-practices/` is worth reading over the next week. Not everything will be relevant yet — read it when you have a question about how something should work.
> - When you add something to the filesystem, update `INDEX.md` in the same commit. This is the one rule that's genuinely non-optional.

Commit a final `"workshop setup complete"` commit covering any remaining open items.

---

## If the user wants to skip steps

That's fine. The most important three are Step 1 (names), Step 2 (writing profile), and Step 4 (first project). The rest can happen when needed. Don't enforce a linear order.
