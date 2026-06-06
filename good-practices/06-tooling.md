# 6. Tooling

The workshop ships with working tools. Here is how to think about when to use which.

## The three compute tiers

**Local (Ollama)** — models running on your own hardware. Free to call once set up, private (your data doesn't leave your machine), slow compared to cloud APIs. Best for bulk mechanical work: translation between languages where local models are adequate, summarization of long documents, classification and tagging, transcript cleanup. The rule for local models: bigger is better, almost without exception. A 125B model running slowly is more useful than a 27B model running fast, because the larger model makes fewer precision errors. Don't use smaller local models to save time — the time you save generating the draft, you spend correcting the errors.

**Session AI (Claude, in this conversation)** — the model you're talking to right now. Best for load-bearing intellectual work: anything that requires your voice, anything that requires synthesis across sources, anything that requires calibrated judgment about a complex question. Don't route mechanical work here — it's slower for bulk tasks and costs more in attention than it's worth.

**Paid API (OpenAI, or whichever frontier provider you have access to)** — second opinion, deep review, tasks where neither local nor session AI can reach the quality bar. Use deliberately. Every call costs real money; log it. Don't default here because it's convenient.

## The routing decision in practice

Before sending any batch task to a model, ask:
- Is this mechanical? (translation, summarization, classification, cleanup) → local Ollama
- Does this require my voice or interpretive judgment? → session AI
- Is this a second opinion or deep review that local can't do? → paid API, with cost awareness

The most common mistake is routing everything to the session AI because it's convenient. This is the vending-machine pattern: you get answers, but you're not building anything. For mechanical tasks, local models running a template are both cheaper and faster.

## Ollama — the local fleet

The `tools/ollama/call.py` helper handles model routing across your local Ollama instances. Before using it, edit the `SERVERS` list at the top of the file to point at your machine. If Ollama is running locally, `localhost:11434` is the default. If you have a dedicated server on your LAN (a Mac Studio running Ollama, a Linux box with a GPU), add its address there.

Always query the model list before writing a task that depends on a specific model:
```bash
python3 tools/ollama/call.py list
```

Don't hardcode model names in scripts — Marc pulls new models regularly, and a script that references `qwen3.5:27b` may be running a worse model than `qwen3.5:122b` without knowing it.

## PDF generation — pandoc + Typst

`/md2pdf` is the skill. It uses pandoc to convert markdown to Typst, then Typst to PDF. The academic template (`academic-template.typ`) handles fonts, margins, citations, and page layout. For most purposes you don't need to touch the template — the skill handles the invocation.

Two things to know about the toolchain: Typst renders faster than LaTeX and requires no installation beyond `brew install typst`. If you have existing LaTeX workflows, you can invoke pandoc with the `--pdf-engine=xelatex` flag instead. The skill supports both.

## Transcription — mlx-whisper

`tools/transcribe/` uses mlx-whisper for local audio transcription. It runs on Apple Silicon natively and is fast enough for practical use. For each audio file, it produces a raw transcript and should be followed by an LLM review pass to catch the characteristic errors (proper nouns, technical terms, language switching). Never cite a transcript without reviewing it first.

## Reference verification — tools/refs-check

Before any paper leaves the workshop, every reference needs verification. `tools/refs-check/check_refs.py` handles this: it queries multiple academic databases (OpenAI, Semantic Scholar, CrossRef, arXiv), checks URL liveness, and retrieves abstracts for comparison. The output is a per-reference verdict: confirmed, title-mismatch, unreachable, or escalate. Any reference that isn't "confirmed" blocks submission.

The hard rule: never invent a URL or DOI to fill in missing metadata. Leave the field empty and let it escalate to you. A paper with a few [URL missing] markers is fixable. A paper with fabricated citations is not.

## Google Workspace — the comms agent's lane

If you set up the comms agent, it uses the `gws` CLI (Google Workspace CLI) for Gmail, Calendar, and Drive access. Setup requires one-time OAuth authentication — see `tools/google/README.md` for the steps. The key constraint: the OAuth scope is read-only. The comms agent can see your calendar and inbox; it cannot send, create events, or modify anything. This is enforced at the credential level.
