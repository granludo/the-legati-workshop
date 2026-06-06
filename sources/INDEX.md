# Sources index

All source material lives under `sources/`. Sources are raw inputs — things you read, watch, or listen to that feed your thinking and writing. They are distinct from your writing projects, which are outputs.

## Structure

```
sources/
├── shared/          ← cross-project sources (papers, books, courses, talks)
│   ├── papers-own/  ← your own published papers (for voice reference + citation)
│   ├── papers-external/  ← reference papers
│   ├── video-and-audio/  ← course recordings, talks, podcasts
│   └── blog-and-writings/  ← your blog posts, essays, manifestos
└── [project-slug]/  ← sources scoped to a single project
```

## How to add a source

Use the `/add-source` skill. It handles:
- **YouTube / video:** transcript extraction → processing → placement
- **PDF:** metadata extraction → text extract → placement
- **Audio:** transcription via mlx-whisper → processing → placement
- **Web article:** fetch → clean → placement
- **Text / paste:** direct placement

Every source gets a `README.md` documenting what it is, where it came from, and what it's for.

## Sources currently indexed

*(none yet — they accrete as you work)*
