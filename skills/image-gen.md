Generate an image via OpenAI's `gpt-image-*` family using `tools/openai/call.py image` and save it to disk. Use this when a writing project or slide deck needs a designed image element — a mock screenshot, a stylised diagram with text burned in, a title card, an illustration — that would be tedious to compose in native shapes and is small enough to be worth a one-shot paid API call.

## When to use this skill

- A slide needs a *designed* visual mixing text and shape (a mock LLM response with a fabricated paper citation, an annotated illustration, a stylised concept diagram).
- A document needs a header image or a one-off illustration.
- A figure that would take more time to compose in PowerPoint / python-pptx / Excalidraw than to specify in a prompt.

## When NOT to use this skill

- **Tables, 2×2 grids, bullet lists, simple shapes** — build these as native PowerPoint elements (python-pptx, Keynote, Excalidraw). They stay editable that way. The unex Día 4 deck (`writting-projects/BSC-AGENTS-COURSE/sources-unex-2026/build_slides_2026-05-13.py`) is the in-repo precedent: simple diagrams native, conceptual diagrams as pre-rendered PNGs.
- **Anything Marc needs to tweak after the fact** — a generated image is a binary; a typo cannot be fixed without regenerating. Native shapes survive editing; images are frozen.
- **Photographs of real people, real places, real products** — use a real photo, not a generation.
- **Anything where the ~$0.16 per high-quality image does not buy enough quality over a 5-minute native composition.**

## Instructions

### 1. Confirm the model is available

The OpenAI image-model lineup moves. Always list first — `list` is free, it just hits `/v1/models`.

```bash
python3 tools/openai/call.py list --filter image
```

Default to `gpt-image-2`. Fall back to whatever is current if it has been deprecated.

### 2. Pick the size

| Size | Aspect | Use for |
|---|---|---|
| `1536x1024` | 3:2 landscape | Slide body image (fits 16:9 with margin) |
| `1024x1024` | 1:1 | Square illustration, icon-style |
| `1024x1536` | 2:3 portrait | Book page figure, half-page illustration |
| `auto` | — | When unsure; the model picks |

### 3. Pick the quality

`high` is the default — appropriate for slides and document figures. Drop to `medium` only for exploratory iteration. `low` is for throwaway tests.

### 4. Write the prompt as a single self-contained paragraph

The model takes a single string. Lead with the medium ("Clean academic slide. Title '…' in dark navy Palatino serif…"). Specify fonts, colours as hex or named, aspect, what NOT to include. See `writting-projects/BSC-AGENTS-COURSE/week-01/session-1-slides.md` for an in-repo prompt library.

### 5. Run the generation

```bash
# Inline prompt
python3 tools/openai/call.py image \
    --model gpt-image-2 \
    --prompt "<your prompt>" \
    --out /path/to/image.png \
    --size 1536x1024 \
    --quality high

# Or read the prompt from a file (cleaner for long prompts)
python3 tools/openai/call.py image \
    --model gpt-image-2 \
    --in prompt.txt \
    --out /path/to/image.png \
    --size 1536x1024
```

`--n 4` generates four variants at once (cheaper per image than four separate calls — the prompt tokens are amortised). Files get `-1.png`, `-2.png`, … suffixes when `--n > 1`.

### 6. Inspect the result

- Did the text render legibly? gpt-image models still occasionally garble small text — re-run with a tighter prompt or larger size if so.
- Does the aesthetic match the rest of the deck / document?
- If wrong: refine the prompt and regenerate. Do not accept a bad image because the call was already paid.

### 7. Surface the cost

Token usage is logged to stderr after every call:

```
[using gpt-image-2, size=1536x1024, quality=high]
[tokens: input=42 (text=42 image=0) output=4160 total=4202]
[wrote 1834 KB to /path/to/image.png]
```

Tell Marc the cost in your summary (a high-quality 1536×1024 image is roughly **$0.15–$0.20** as of early 2026).

## Prompt patterns that work

- **Lead with the medium.** *"Clean academic slide. Title '…' in dark navy Palatino serif. Below, …"*
- **Specify font family even if the model cannot honour it exactly.** Names like "Palatino serif", "Helvetica sans-serif", "Consolas monospace" anchor the aesthetic.
- **Spell out colour as hex or named.** *"navy #1F2454 on white background"*.
- **Specify aspect and decoration explicitly.** *"16:9. No decoration. Thin navy lines only."*
- **Be explicit about what NOT to include.** *"No drop shadows. No gradients. No emoji."*

## Failure modes

- **`404 model not found`** — `gpt-image-2` has been renamed / deprecated. Re-run `list --filter image` and pick the current id.
- **Garbled text in the output** — common with small fonts / long titles. Increase size, shorten the text-burned-in portion, or split: keep editable text native and put only the genuinely-illustrative portion in the image.
- **`429` rate limit** — retry once with backoff, then tell Marc.

## Cross-references

- Helper (the `image` subcommand): [`tools/openai/call.py`](../tools/openai/call.py)
- Helper README: [`tools/openai/README.md`](../tools/openai/README.md)
- Infrastructure reference: [`memory/reference_openai_api.md`](../memory/reference_openai_api.md)
- Compute routing tiers in [`CLAUDE.md`](../CLAUDE.md)
