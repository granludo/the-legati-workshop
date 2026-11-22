# tools/llm: the `llm` front door

Every model call that is **not** the session model (a local model for bulk work, a second frontier model for an independent opinion, embeddings) goes through [Simon Willison's `llm` command](https://llm.datasette.io). One command surface for every provider, and every prompt and response **logged to SQLite** automatically, so you can always see what was asked of which model and what came back. This works the same from Claude Code, from Codex and from your own terminal.

## Setup (once per machine)

```bash
uv tool install llm                # or: pipx install llm · brew install llm
llm install llm-ollama             # local models through Ollama (optional)
llm keys set openai                # paste your key; stored in llm's keys.json, outside the repo (optional)
llm models                         # what you can call now
```

Other providers are plugins too (`llm install llm-anthropic`, `llm install llm-gemini`, `llm install llm-mistral` …). A remote Ollama server on your network: `OLLAMA_HOST=http://desk-machine.local:11434` in your shell profile. Record what this machine has in its section of `memory/reference_hosts.md`.

Aliases keep prompts short and make routing explicit:

```bash
llm aliases set local qwen3.5:122b # whatever big model your Ollama server runs
llm aliases set second gpt-5       # a frontier model from another family
```

## Use

```bash
llm -m local 'Summarise this transcript in five bullet points' < transcript.txt
cat draft.md | llm -m second -s 'Review this argument. List the three weakest claims.'
llm embed -m nomic-embed-text -c 'text to embed'
```

Common flags: `-s 'system prompt'` · `-o temperature 0.2` · `-o max_tokens 4000` · `-a image.png` (vision models) · `-t <template>`.

## Routing rules

- **Interpretive, voice-sensitive and load-bearing work stays on the session model.** That includes anything that must sound like the principal.
- **Bulk mechanical work** (classification, extraction, summaries for your own use, first-pass translation drafts in languages the model handles well) can go to a large local model. Prefer big models: small ones degrade fast on long contexts and outside English.
- **Never send generation in a language to a model that writes it badly.** For many local models that means Catalan, Basque, Galician and other smaller languages: those stay on the session model or a frontier model.
- **Paid calls cost real money:** be deliberate, and say before a batch how many calls it will make.
- **Long calls follow the progress rule** (`memory/feedback_progress_updates.md`).
- **Always pass `-m`** so the route is visible in the command and in the log.

## The log

```bash
llm logs path            # where the SQLite database lives (per machine, outside the repo)
llm logs -n 5            # last five responses
llm logs -q "search"     # full-text search over prompts and responses
llm logs -m local -n 10  # filter by model
```

The database contains prompt text: treat it like `.env`, local working state that never enters git. Browse it with `uvx datasette "$(llm logs path)"`.

## What this replaces

`tools/ollama/call.py` and `tools/openai/call.py` stay only for the scripts that already call them (`tools/wiki/`, `skills/image-gen.md` for images). New scripts call the `llm` command or its Python API (`import llm`), so their calls land in the log too. Keys never enter git: they live in `llm keys` or in `.env` (gitignored).
