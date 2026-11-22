# tools/ollama/

> [!note] Prefer `llm`
> New work calls models through the `llm` command ([tools/llm/README.md](../llm/README.md)), which also reaches Ollama through the `llm-ollama` plugin and logs every call. This helper stays for the scripts that already use it (`tools/wiki/`).

Helper for one or more Ollama servers: a big desktop machine on your network, or `localhost`. Edit the `SERVERS` list at the top of `call.py` with your addresses (the shipped values are the original workshop's LAN and will not answer on yours).

The helper probes the servers in order and picks the first reachable one that has the requested model. Prefer large models: small local models degrade quickly on long contexts and on languages other than English.

## Quick use

```bash
# List models across the whole fleet (shows which server has what)
python3 tools/ollama/call.py list

# List models on a specific server
python3 tools/ollama/call.py --server http://localhost:11434 list

# Generate with whatever server has the model (fleet auto-discovery)
python3 tools/ollama/call.py generate --model gpt-oss:20b --prompt "Hola, com estàs?"

# Generate from a file, write to a file
python3 tools/ollama/call.py generate \
    --model qwen3.5:122b \
    --in sources/ia-i-educacio/el-moment-sputnik-2024/el_moment_sputnik_2024.txt \
    --out /tmp/summary.md \
    --temp 0.2

# Force a specific server (e.g. for benchmarking)
python3 tools/ollama/call.py --server http://localhost:11434 generate \
    --model qwen3.5:122b --prompt "test"

# Generate embeddings (only on .47 today)
python3 tools/ollama/call.py embed \
    --model nomic-embed-text:latest \
    --in some-text.txt
```

Zero dependencies — uses only stdlib `urllib`. Runs with plain `python3` or via `uv run`.

## When it fails

Two failure modes:

**Exit code 2 — all servers unreachable.** No server in `SERVERS` answered the probe. Usually this machine is off the network where the server lives (a laptop on conference Wi-Fi), or the server is off.

```
ERROR: no Ollama server reachable. Tried: <your SERVERS list>
HINT:  Fall back to the session model for this task and tell the principal you fell back.
```

**Exit code 3 — model not available.** A server was reachable but didn't have the requested model. The helper prints what's actually available so you can pick an alternative.

**Fallback protocol:** when a calling agent (Claude) sees exit code 2:
1. Tell the principal it fell back to the session model.
2. Do the task directly in the current conversation.
3. Not silently degrade, not retry in a loop.

When the agent sees exit code 3: run `list` to see the current fleet, pick a sensible alternative, retry once. If still unavailable, tell the principal.

## Context window policy

In the original workshop's experience, **small models** (under 70B params) degrade when context goes above ~64k, so the helper caps `num_ctx` at 65536 for those. Larger models (70B+) use their default (which on this server is set high). Override with `--num-ctx N` if you know what you're doing.

## Timeouts

Default 900 seconds (15 min). Local models are slow on first call (warmup) and slow on long generations. If that's not enough, override with `TIMEOUT_SECONDS` in `call.py` or pass a shorter prompt.

## Dynamic model discovery

Models change on the servers over time. **Always run `list` first** to see what's currently available instead of assuming a specific model exists. Today's models may differ from yesterday's — and which server has which model can change between pulls.

## When to route tasks here vs. Claude Opus

**Use local Ollama (Qwen 3.5 122B or whatever the current "fast" model is) for:**
- Routine translation drafts (CA ↔ ES ↔ EN, will be rewritten by the principal)
- Summarization of long source material
- Classification / tagging
- Transcription cleanup (fixing named entities, removing hallucinations)
- Initial outline skeletons the principal will overwrite
- Bulk text operations (regex isn't enough, semantics is enough)

**Use Opus for:**
- Anything requiring the principal's voice (needs writing profile + worldview)
- Intellectual synthesis, cross-domain reasoning
- Editorial dialogue with the principal
- Final drafts of chapters and papers
- Decisions and structural tradeoffs

**Rule of thumb:** if a task is *mechanical and voluminous*, Ollama. If it's *interpretive and load-bearing*, Opus.

## Memory pointer

See [../../memory/reference_ollama_server.md](../../memory/reference_ollama_server.md) for the canonical infrastructure reference, kept in sync with any model/server changes.
