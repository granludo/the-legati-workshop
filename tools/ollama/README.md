# tools/ollama/

Helper for Marc's local Ollama **fleet** — two **stationary** Mac Studios on the home LAN:

- **`http://192.168.1.35:11434`** (`tom-nook-studio.local`) — Mac Studio M3 Ultra 512 GB, always on. Runs `qwen3.5:122b` plus smaller models (smaller ones are forbidden by the big-guns rule).
- **`http://192.168.1.47:11434`** (`studio64.local`) — Mac Studio M2 Ultra 192 GB, also stationary, normally on. Runs `qwen3.5:122b` and the only embedding model (`nomic-embed-text`).

Both servers stay up. The roving **MacBook** is on DHCP — when off the home LAN, neither Studio is reachable from that session, but the Studios themselves are fine.

The helper auto-discovers both and picks the first reachable one that has the requested model.

## Quick use

```bash
# List models across the whole fleet (shows which server has what)
python3 tools/ollama/call.py list

# List models on a specific server
python3 tools/ollama/call.py --server http://192.168.1.35:11434 list

# Generate with whatever server has the model (fleet auto-discovery)
python3 tools/ollama/call.py generate --model gpt-oss:20b --prompt "Hola, com estàs?"

# Generate from a file, write to a file
python3 tools/ollama/call.py generate \
    --model qwen3.5:122b \
    --in sources/ia-i-educacio/el-moment-sputnik-2024/el_moment_sputnik_2024.txt \
    --out /tmp/summary.md \
    --temp 0.2

# Force a specific server (e.g. for benchmarking)
python3 tools/ollama/call.py --server http://192.168.1.47:11434 generate \
    --model qwen3.5:122b --prompt "test"

# Generate embeddings (only on .47 today)
python3 tools/ollama/call.py embed \
    --model nomic-embed-text:latest \
    --in some-text.txt
```

Zero dependencies — uses only stdlib `urllib`. Runs with plain `python3` or via `uv run`.

## When it fails

Two failure modes:

**Exit code 2 — all servers unreachable.** Both `.35` and `.47` didn't respond to the probe. Both Studios are stationary and normally on, so this usually means *this session is off the home LAN* (roving MacBook on conference Wi-Fi or hotspot). Less commonly: home network down, or a Studio off for maintenance.

```
ERROR: no Ollama server reachable. Tried: http://192.168.1.35:11434, http://192.168.1.47:11434
HINT:  Both Studios (.35 / tom-nook-studio and .47 / studio64) are stationary
       and normally on. "Both unreachable" usually means *this session is
       off the home LAN* (roving MacBook on conference Wi-Fi or hotspot) —
       the servers themselves stay up. Less commonly: home network down or
       a Studio off for maintenance.
       Fall back to Claude for this task and tell Marc you fell back.
```

**Exit code 3 — model not available.** A server was reachable but didn't have the requested model. The helper prints what's actually available so you can pick an alternative.

**Fallback protocol:** when a calling agent (Claude) sees exit code 2:
1. Tell Marc it fell back to Claude.
2. Do the task directly in the current conversation.
3. Not silently degrade, not retry in a loop.

When the agent sees exit code 3: run `list` to see the current fleet, pick a sensible alternative, retry once. If still unavailable, tell Marc.

## Context window policy

Marc reports that **small models** (under 70B params) degrade when context goes above ~64k, so the helper caps `num_ctx` at 65536 for those. Larger models (70B+) use their default (which on this server is set high). Override with `--num-ctx N` if you know what you're doing.

## Timeouts

Default 900 seconds (15 min). Local models are slow on first call (warmup) and slow on long generations. If that's not enough, override with `TIMEOUT_SECONDS` in `call.py` or pass a shorter prompt.

## Dynamic model discovery

Marc pulls new models periodically across both servers. **Always run `list` first** to see what's currently available instead of assuming a specific model exists. Today's models may differ from yesterday's — and which server has which model can change between pulls.

## When to route tasks here vs. Claude Opus

**Use local Ollama (Qwen 3.5 122B or whatever the current "fast" model is) for:**
- Routine translation drafts (CA ↔ ES ↔ EN, will be rewritten by Marc)
- Summarization of long source material
- Classification / tagging
- Transcription cleanup (fixing named entities, removing hallucinations)
- Initial outline skeletons Marc will overwrite
- Bulk text operations (regex isn't enough, semantics is enough)

**Use Opus for:**
- Anything requiring Marc's voice (needs writing profile + worldview)
- Intellectual synthesis, cross-domain reasoning
- Editorial dialogue with Marc
- Final drafts of chapters and papers
- Decisions and structural tradeoffs

**Rule of thumb:** if a task is *mechanical and voluminous*, Ollama. If it's *interpretive and load-bearing*, Opus.

## Memory pointer

See [../../memory/reference_ollama_server.md](../../memory/reference_ollama_server.md) for the canonical infrastructure reference, kept in sync with any model/server changes.
