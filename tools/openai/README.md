# tools/openai/

Helper for OpenAI's API — parallel to `tools/ollama/call.py`. Same CLI shape, different backend.

Use this when a task needs **frontier-quality reasoning** that local Ollama can't reach AND the call is worth real money. For routine/voluminous work stay on Ollama. For Marc's voice and editorial dialogue stay on Claude (current conversation).

## Quick use

```bash
# List currently available models (free — uses /v1/models)
python3 tools/openai/call.py list

# Filter the model list (substring, case-insensitive)
python3 tools/openai/call.py list --filter gpt-5
python3 tools/openai/call.py list --filter o3

# Generate from an inline prompt
python3 tools/openai/call.py generate --model gpt-5.4 --prompt "..."

# Generate from a file → file
python3 tools/openai/call.py generate \
    --model gpt-5.4 \
    --in /path/to/chapter.md \
    --out /tmp/review.md \
    --system "You are a critical editor of long-form essays. Identify weak passages and propose specific cuts."

# System prompt from a file (recommended for long review prompts)
python3 tools/openai/call.py generate \
    --model gpt-5.4-pro \
    --in /path/to/chapter.md \
    --out /tmp/review.md \
    --system /path/to/review-system-prompt.md

# Reasoning model (o-series)
python3 tools/openai/call.py generate \
    --model o3-pro \
    --in /path/to/chapter.md \
    --out /tmp/review.md \
    --reasoning-effort high
```

Zero dependencies — uses only stdlib `urllib`. Runs with plain `python3`.

## API key

The helper reads the API key from, in order:
1. Environment variable `OPENAI_API_KEY` (canonical, matches the OpenAI SDK)
2. Environment variable `openai_api_key` (lowercase fallback)
3. The repo's `.env` file (also case-insensitive — `OPENAI_API_KEY` or `openai_api_key`)

The key is **never printed or logged** — not even in error messages. The `.env` file is gitignored (verified).

If the key is missing or invalid, the helper exits with code 2 and a clear hint. It will not silently degrade.

## When to route tasks here vs. Ollama vs. Claude

This is the third tier in the compute routing rules. The first two are documented in [memory/reference_ollama_server.md](../../memory/reference_ollama_server.md).

**Use OpenAI (this helper) for:**
- **Frontier-quality second opinion / review.** Take a chapter draft, run it through GPT-5.4 or o3-pro with a critical-editor system prompt, get a structured critique. Pair with the writing profile + density rules for calibration.
- **Deep reasoning tasks** where local Ollama models visibly hit a ceiling and getting the right answer matters. Reasoning models (o3-pro, o4-mini-deep-research) for problems with verifiable structure.
- **Complex multilingual nuance** where the local 122B Qwen falls short on specific Catalan/Spanish idioms or cultural register.
- **Anything where Marc said "use the highest performance model".**

**Stay on Ollama (`tools/ollama/call.py`) for:**
- Routine translation drafts
- Bulk summarization of long source material
- Classification, tagging, transcription cleanup
- First-pass outlines Marc will rewrite
- Anything mechanical and voluminous where the output is raw material

**Stay on Claude Opus (current conversation) for:**
- Anything that needs to BE in Marc's voice (final drafts, chapter rewrites)
- Editorial dialogue with Marc
- Structural decisions and tradeoffs
- Anything load-bearing where getting it wrong would silently damage a document Marc trusts

**Rule of thumb:**
- *mechanical and voluminous* → Ollama (free, local)
- *interpretive and load-bearing in Marc's voice* → Claude (current session)
- *frontier reasoning, second opinion, deep critique* → OpenAI (paid)

## Cost

OpenAI calls cost real money. Token usage is logged to stderr after every call:

```
[using gpt-5.4]
[tokens: prompt=12453 completion=2891 total=15344]
```

For reasoning models, reasoning tokens are reported separately because they're billed differently:

```
[tokens: prompt=12453 completion=8421 (reasoning=5530) total=20874]
```

Be deliberate. A `gpt-5.4-pro` review of a 30k-token chapter at high reasoning effort is not cheap. When in doubt, run on a smaller sample first.

## Model selection

**Always run `list` first.** The available model lineup changes month to month. Don't hardcode model names in scripts; check what's there.

```bash
python3 tools/openai/call.py list --filter gpt-5
```

As a snapshot from when this helper was first written (2026-04-11):

| Tier | Model | Use for |
|---|---|---|
| Flagship | `gpt-5.4` | General high-quality review, chapter critique |
| Flagship pro | `gpt-5.4-pro` | The most thorough review — slow, expensive, best |
| Flagship mini | `gpt-5.4-mini` | Faster/cheaper iteration on the same task |
| Reasoning | `o3-pro` | Deep critical analysis with reasoning trace |
| Reasoning long | `o3-deep-research` / `o4-mini-deep-research` | Multi-step research/synthesis tasks |
| Codex | `gpt-5.4` (or `gpt-5.3-codex`) | Code review |

This snapshot will go stale within weeks. Re-run `list` instead of trusting it.

## Reasoning models

For o-series models (o3, o3-pro, o4-mini, etc.), pass `--reasoning-effort low|medium|high`.

Reasoning models may reject `--temp` and behave differently around `--max-tokens`. If the API returns an error about an unsupported parameter, drop it and retry once.

## Image generation

The helper exposes the `image` subcommand for the `gpt-image-*` model family. Same key, same `.env` resolution, same error handling as the chat path. The `image` subcommand hits `/v1/images/generations` and writes the resulting PNG (base64-decoded by the helper) to `--out`.

```bash
# List image models
python3 tools/openai/call.py list --filter image

# Generate one image
python3 tools/openai/call.py image \
    --model gpt-image-2 \
    --prompt "Clean academic slide. Title '...' in dark navy Palatino serif. ..." \
    --out /tmp/slide.png \
    --size 1536x1024 \
    --quality high

# Multiple variants on one prompt (cheaper per image — shared prompt tokens)
python3 tools/openai/call.py image \
    --model gpt-image-2 \
    --in prompt.txt \
    --out /tmp/slide.png \
    --n 4
# → /tmp/slide-1.png, /tmp/slide-2.png, /tmp/slide-3.png, /tmp/slide-4.png
```

Flags:
- `--size`: `1024x1024` (square) · `1536x1024` (landscape, fits 16:9 slides) · `1024x1536` (portrait) · `auto`
- `--quality`: `low | medium | high (default) | auto`
- `--n`: number of variants (default 1; files suffixed `-1`, `-2`, …)
- `--output-format`: `png | jpeg | webp` (model default if omitted)
- `--background`: `transparent | opaque | auto` (transparent works with `png`/`webp`)

Cost as of early 2026: a `high`-quality 1024×1024 or 1536×1024 runs roughly **$0.15–$0.20** per image. Usage is logged to stderr the same way chat usage is.

Full skill for when-to-use and prompt patterns: [`../../skills/image-gen.md`](../../skills/image-gen.md).

## Failure modes

**Exit code 1** — empty prompt or other usage error.

**Exit code 2** — API/network failure. The helper prints the API's error message (truncated to 1000 chars) and exits. Do not silently retry. **Tell Marc** when this happens, the same way the Ollama helper's fallback protocol works.

The most common causes:
- Missing or invalid API key (`401 unauthorized`) — check `.env`
- Model name typo (`404 model not found`) — run `list` to see what exists
- Rate limit (`429`) — retry once with backoff, then tell Marc
- Context too long (`400`) — split the input or use a model with bigger context

## Memory pointer

See [`../../memory/reference_openai_api.md`](../../memory/reference_openai_api.md) for the canonical infrastructure reference, kept in sync with any model lineup changes Marc reports.
