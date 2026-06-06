---
name: add-source
description: Intake a new source (YouTube video, PDF, audio file, web article, text) into the ludo-writting-workshop sources/ tree for a specific writing project or shared use. Handles download, audio extraction, transcription, placement, README, and INDEX.md registration.
---

# /add-source

Use this when Marc wants to bring new source material into the repo. The skill handles the full intake pipeline: acquire → derive → place → document → register. It is **conservative by design** — it lands the source and offers to link it into project docs, but does not auto-edit project wikis or memory. Integration is a separate step Marc approves.

## When to invoke

Marc says things like:
- "add this source: <URL>"
- "/add-source <URL or path>"
- "I found this paper, can you put it in the right place"
- "here's a new conference recording for the ia-i-educacio book"

## Inputs

Accept any of the following, and auto-detect the type:
- **YouTube URL** → use `yt-dlp` (already installed in this environment).
- **Web article / academic paper URL** (PDF or HTML) → use `curl` or `WebFetch`. Always prefer downloading the PDF if the page offers one.
- **Local PDF or other binary** → move/copy into the target location.
- **Local audio or video file** → same, with derived audio/transcription steps.
- **Pasted text / markdown** → write directly to a `.md` file under the right folder.

If the input is ambiguous (e.g. a bare filename), ask Marc before proceeding.

## Pipeline (follow in order)

### 1. Identify scope

Ask Marc (or infer from context) which scope the source belongs to:
- **`sources/shared/<type>/`** if it feeds multiple projects or is of general interest.
- **`sources/<project>/`** if it only makes sense for one specific writing project. Valid project slugs today: `ia-i-educacio`, `palantir-paper`, `aprenentatge-personalitzat`, `aac-book`.

If you're unsure, **default to `shared/`**. It's easier to silo later than to un-silo now.

### 2. Choose a folder slug

Create a folder under the chosen scope with a lowercase kebab-case name. Conventions:
- **Talks / conferences:** `{year}-{venue}-{topic}` — e.g. `2024-udl-sputnik/`.
- **Books / articles:** `{firstauthor}-{year}-{shortname}` — e.g. `weller-2022-metaphors/`.
- **Courses / masterclasses:** `{name}-{subtitle}` — e.g. `lamb-101-rag-masterclass/`.
- **Blog posts / single-file sources:** no folder — put the file directly under the scope with a descriptive name.

For a multi-file source (video + audio + transcript + metadata), always use a folder. For a single self-contained PDF, drop it directly under the scope.

### 3. Acquire the bytes

**YouTube URL:**
```bash
cd <scope-folder>
yt-dlp --write-info-json --write-subs --write-auto-subs \
       --sub-langs "ca,es,en,ca.*,es.*,en.*" \
       -f "bv*+ba/b" \
       -o "%(title)s.%(ext)s" "<URL>"
```
If ffmpeg is not installed system-wide, yt-dlp will leave separate video/audio streams — that's fine. The actual audio for transcription will be in the `.webm` (Opus) or `.m4a` file.

**Web URL (PDF):**
```bash
curl -sSL -o <filename>.pdf "<URL>"
```

**Web URL (HTML article):** use `WebFetch` with a prompt asking for the article text in markdown, then save the result.

**Local file:** `mv` or `cp` into place.

### 4. Derive useful formats

**Video → audio (MP3 for transcription/listening):**
```bash
uv run --with imageio-ffmpeg python -c "
import imageio_ffmpeg, subprocess
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([ffmpeg, '-y', '-i', 'input.webm', '-vn',
                '-codec:a', 'libmp3lame', '-b:a', '128k', '-ar', '44100',
                'output.mp3'])
"
```

**Audio → transcription:** use the existing repo tool.
```bash
uv run --project tools/transcribe tools/transcribe/transcribe.py --lang ca <audio.mp3>
```
(Substitute `--lang es` or `--lang en` as appropriate.) This writes `.srt` and `.txt` next to the input. Language is detected from context — if Marc doesn't specify, ask.

**Mandatory LLM review pass on the transcript.** Whisper produces blatant blunders — proper nouns, acronyms, code-switch, in-group vocab — at a high enough rate that the raw `.txt` must not be treated as citation-ready. Keep the raw file as the audit trail and produce a `<slug>.reviewed.txt` via an LLM pass. Model tier follows the writing rules: CA content → Claude (this conversation) or `tools/openai/call.py` with gpt-5; ES/EN content → DS4 on tom-nook (see `memory/reference_ds4_server.md`) for mechanical proper-noun correction, frontier review when the content is load-bearing. The reviewed file should flag what was changed (head section for short transcripts, inline `==highlight==` for long ones) so Marc can spot-check. Full rule and rationale: [../memory/feedback_whisper_transcripts_need_llm_review.md](../memory/feedback_whisper_transcripts_need_llm_review.md).

**PDF:** keep as-is. If text extraction is useful, mention it as an *optional* follow-up; don't do it by default.

### 5. Write a `README.md` inside the source folder

For any **multi-file source**, create a `README.md` with:

```markdown
# <Source title>

- **Type:** <conference | paper | blog post | video course | ...>
- **Author / speaker:** <...>
- **Origin:** <original URL or citation>
- **Date of material:** <YYYY-MM-DD or year>
- **Date added to repo:** <YYYY-MM-DD>
- **Language:** <ca | es | en | ...>
- **Project(s) it feeds:** <list of writing projects that reference this>

## Summary
<One paragraph describing what this source contains and why it was added.>

## Files in this folder
- `<filename>` — <one-line description>
- ...

## Notes
<Anything quirky: transcription quality, missing subtitles, trailing hallucinations, OCR issues, pages to skip, etc.>
```

Single-file sources don't need their own README — their entry in `sources/INDEX.md` does the job.

### 6. Register in `sources/INDEX.md`

Add an entry under the right section (either `shared/<type>/` or `<project>/`). Match the existing format: a bullet with filename/folder name in backticks, followed by a one-line description and any critical metadata.

**If a section for this scope doesn't exist yet**, create it in alphabetical order alongside the existing ones, and use the same heading style.

**Deduplication check:** before landing the source, grep `sources/INDEX.md` for the origin URL, title, or filename. If there's a match, stop and tell Marc rather than ingesting twice.

### 7. Offer integration (do not auto-apply)

Once the source is in place and indexed, **offer** to:
- Add a pointer in the relevant project document (e.g. §16 of `writting-projects/ia-i-educacio/idees_ia_i_educacio.md`).
- Update the project's `BACKLOG.md` with a follow-up task like "read X and decide whether it feeds chapter Y".
- Update the project's memory with a new fact if the source changes the state of the world.

**Wait for confirmation** before doing any of those. The reason: the domain-separation feedback in `memory/feedback_domain_separation.md` and the v3-overboard feedback in `memory/feedback_v3_overboard.md` warn against forcing references across project domains. Let Marc decide which project(s) actually want the pointer.

### 7.5 Offer wiki integration (also gated, also conservative)

After the source is landed and indexed, **offer** to walk it through the wiki ingest. The pipeline:

```bash
# Always dry-run first — shows the proposed change set, writes nothing.
python3 tools/wiki/ingest.py <source-rel-path>
```

The dry-run reports:
- the extraction summary the model produced (2-3 sentences),
- existing wiki entries that would gain a timeline pointer,
- new entries that would be scaffolded (with their proposed slug),
- entries already linked from the source (idempotent — already-ingested sources skip cleanly).

Surface the dry-run output to Marc. If Marc approves, apply:

```bash
python3 tools/wiki/ingest.py --apply <source-rel-path>
```

Then run the two regen scripts so cross-refs and INDEXes reflect the new entries:

```bash
python3 tools/wiki/build_cooccurrence.py
python3 tools/wiki/render_indexes.py
```

If Marc skips, that's fine — the source still lives under `sources/` and can be ingested later in a batch via `tools/wiki/bootstrap.py --resume`.

**Why gated, not auto:** the extractor sometimes proposes new person/topic slugs that are variants of existing entries (e.g. `juan-antonio-pereira` when `juanan-pereira` already exists). Marc should eyeball the new-scaffold list before it lands so duplicates don't accrete. The same caution applies to topics — the extractor occasionally tags broader generic categories that the wiki has already declined to canonicalize.

### 8. Report

End with a short report to Marc:
- What was added (scope + path).
- What was derived (audio, transcription, etc.).
- What was skipped (if anything, and why).
- What integration was offered but not applied.

## What this skill does NOT do

- **Does not** edit project drafts, book wikis, or memory files without explicit confirmation.
- **Does not** move or rename files that are already in `sources/`. If something needs to move between scopes, that's a separate task.
- **Does not** delete the original after successful derivation. The archive policy is "preserve everything"; the original webm/mp4 stays alongside the derived mp3/txt.
- **Does not** guess at Marc's voice. If you summarize a source in its README, keep it factual and under 100 words. Summaries with opinions or framings belong in the project documents, where Marc can rewrite them.

## Related

- [../sources/INDEX.md](../sources/INDEX.md) — the index this skill maintains.
- [../tools/transcribe/transcribe.py](../tools/transcribe/transcribe.py) — the transcription script this skill calls.
- [../tools/wiki/ingest.py](../tools/wiki/ingest.py) — the single-source wiki ingest tool referenced in step 7.5.
- [../memory/feedback_index_maintenance.md](../memory/feedback_index_maintenance.md) — why the index must stay current.
