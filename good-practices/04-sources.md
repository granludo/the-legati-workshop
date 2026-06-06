# 4. Source management

A source is raw material — a paper, a recording, a video, a book chapter, a web article. Sources are not outputs. They feed your thinking; they are not your thinking. The distinction sounds obvious, but the workflow consequences are significant.

The `sources/` folder is not a library. It's a processing queue with long-term storage. Something enters as a source, gets processed into usable form, and then sits as a citable, searchable resource for future sessions. If it doesn't get processed, it's just a file accumulating dust.

## The processing pipeline

Every source that enters the workshop goes through the `/add-source` skill. That skill handles the mechanics: transcript extraction for video and audio, text extraction for PDFs, clean retrieval for web articles. What it produces is not just a copy of the source — it's the source plus metadata: where it came from, when you acquired it, what it's for, key claims or passages you flagged.

The reason for this discipline: a source that's just a PDF or a transcript is hard to use in a session. A source that's been processed — with a summary, with key passages extracted, with a README that explains why you cared about it — is immediately useful. The three minutes of processing saves ten minutes of search across twenty sessions.

## Whisper transcripts need review

If you process audio or video through automatic transcription, never trust the transcript directly. Automatic speech recognition makes characteristic errors: proper nouns, technical terms, in-group vocabulary, language-switching. It often mishears the specific words that matter most. Run a review pass before citing anything from a transcript. For your own language, a quick skim is enough; for technical content, a more careful pass.

## The shared vs. per-project split

Sources that a single project needs go in `sources/[project-slug]/`. Sources that multiple projects might draw on go in `sources/shared/`. When a source migrates from one project to shared, update both `INDEX.md` files.

Don't be too clever about the split. When in doubt, put it in the project folder. Premature sharing creates confusion about who owns the source and whether updates affect other projects.

## Your own past work

Your own published papers belong in `sources/shared/papers-own/`. This sounds redundant — you know what you wrote — but it has a specific purpose: giving the writing agent concrete examples of your voice and your argument style in their final, published form. The writing profile describes your voice abstractly; your own papers instantiate it. When the agent is struggling to match your register, reading three of your papers is more effective than re-reading the writing profile.

## The citation discipline

Sources feed citations. Citations require verification. Before any paper leaves the workshop, every reference should have a verified DOI or URL and a confirmed match between the title/authors you're citing and the actual document. The `/refs-check` tooling handles most of this automatically. The rule is: never invent a URL or DOI to fill in missing metadata — leave the field empty and escalate to yourself. A broken citation is better than a fabricated one.
