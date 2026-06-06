# /write-as-[you] — load your writing profile

**When to invoke:** before any writing task. The Writer agent loads your writing profile so output sounds like you, not like a generic AI.

**Who runs it:** the Writer agent.

> [!todo] You
> This skill file is a template. Before using it:
> 1. Write `principals/[your-name]/writing-profile.md` — the document that teaches agents your voice.
> 2. Rename this file to `write-as-[your-name].md` (e.g., `write-as-alice.md`).
> 3. Update the path in step 1 below to match your file.
> 4. Update the skill table in `CLAUDE.md` to point at the renamed file.

---

## What to do

1. Read `principals/[your-name]/writing-profile.md` in full.
2. Confirm to the user: "Writing profile loaded — ready to write as [your name]."
3. Apply the profile to everything you write this session until told otherwise.

## What this means in practice

- Match the voice, tone, and rhythm described in the profile.
- Use the domain-specific register for the domain you're working in.
- Apply the structural patterns (how the user opens, closes, structures arguments).
- Avoid the explicit "what to avoid" list.
- Do not add features, caveats, or sections the user did not ask for.
- If the profile says first-draft-in-English, do that regardless of the target language.

## When the profile is thin or new

The profile grows over time. If it's sparse, write the best approximation you can and flag to the user what you guessed — so they can add to the profile.

## The profile is not a cage

The profile captures patterns, not rules. If a specific piece calls for a departure from the usual register (e.g., a formal grant proposal when the user usually writes colloquially), note the departure and ask before proceeding.
