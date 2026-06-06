#!/usr/bin/env python3
"""
tools/ollama/call.py — thin helper for local Ollama servers.

Zero dependencies (uses stdlib urllib). Runs with plain python3 or via uv.

Usage:
    python3 tools/ollama/call.py list
    python3 tools/ollama/call.py generate --model MODEL --prompt "..."
    python3 tools/ollama/call.py generate --model MODEL --in prompt.txt --out result.md
    python3 tools/ollama/call.py embed --model nomic-embed-text:latest --in text.txt

    # Target a specific server explicitly:
    python3 tools/ollama/call.py --server http://localhost:11434 list

Server discovery:
    By default the helper probes SERVERS in order and uses the first one
    that is reachable. `list` shows models from EVERY reachable server so
    you can see what's available across the fleet.

    For `generate` and `embed`, if you don't pass --server, the helper
    picks the first reachable server that has the requested model
    available — so a batch job is resilient to one server being down.

Error handling:
    On total connection failure (no server reachable) the helper prints
    a clear ERROR + HINT to stderr and exits with code 2. The calling
    agent should interpret this as "all Ollama servers down — fall back
    to the session AI."

Context window policy:
    Models under 70B parameters are capped at 64k context by default.
    Larger models (70B+) get the model's default context unless --num-ctx
    is passed explicitly.

Timeouts:
    Default 900s (15 minutes) — local models are slow and we don't want
    to fail mid-generation on a long summarization.

Configuration:
    Edit the SERVERS list below to point at your Ollama instance(s).
    Localhost is the default. For a network server, use its LAN address.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

# In priority order. First reachable server wins unless --server overrides.
# Edit this list to match your Ollama setup.
# Tip: add your LAN server address before localhost if you have a dedicated Ollama machine.
SERVERS = [
    "http://localhost:11434",       # local — change to your Ollama server address
    # "http://192.168.1.X:11434",  # example: a LAN machine running Ollama
]
PROBE_TIMEOUT = 5
TIMEOUT_SECONDS = 900  # 15 minutes for generation
SMALL_MODEL_CTX = 65536  # 64k cap for models <70B params
LARGE_MODEL_THRESHOLD_B = 70.0


def _probe(base_url: str) -> list[dict] | None:
    """Return the list of models on a server, or None if unreachable."""
    try:
        req = urllib.request.Request(f"{base_url}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=PROBE_TIMEOUT) as resp:
            return json.loads(resp.read()).get("models", [])
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ConnectionError):
        return None


def _fleet(explicit_server: str | None) -> list[tuple[str, list[dict]]]:
    """Return [(base_url, models)] for servers we can reach right now."""
    servers_to_try = [explicit_server] if explicit_server else SERVERS
    fleet: list[tuple[str, list[dict]]] = []
    for base in servers_to_try:
        models = _probe(base)
        if models is not None:
            fleet.append((base, models))
    return fleet


def _pick_server_for_model(model: str, explicit_server: str | None) -> str:
    """Pick the first reachable server that has `model` loaded."""
    if explicit_server:
        models = _probe(explicit_server)
        if models is None:
            _die_all_unreachable([explicit_server])
        if model not in {m["name"] for m in models}:
            print(
                f"ERROR: server {explicit_server} does not have model '{model}'. "
                f"Available: {sorted(m['name'] for m in models)}",
                file=sys.stderr,
            )
            sys.exit(3)
        return explicit_server

    reachable_any = False
    for base in SERVERS:
        models = _probe(base)
        if models is None:
            continue
        reachable_any = True
        if model in {m["name"] for m in models}:
            return base
    if not reachable_any:
        _die_all_unreachable(SERVERS)
    print(
        f"ERROR: no reachable server has model '{model}'. Run `list` to see what's available.",
        file=sys.stderr,
    )
    sys.exit(3)


def _die_all_unreachable(tried: list[str]) -> None:
    tried_str = ", ".join(tried)
    print(
        f"ERROR: no Ollama server reachable. Tried: {tried_str}\n"
        f"HINT:  Check that your Ollama server is running. If you're on a laptop\n"
        f"       away from home, your LAN Ollama server may be unreachable — the\n"
        f"       server itself is up, but this session can't reach it from outside.\n"
        f"       Edit the SERVERS list in this file to match your network topology.\n"
        f"       Fall back to the session AI and tell the user you fell back.",
        file=sys.stderr,
    )
    sys.exit(2)


def _request(path: str, payload: dict | None = None, method: str = "GET",
             timeout: int = TIMEOUT_SECONDS, base_url: str | None = None):
    if base_url is None:
        raise ValueError("base_url is required")
    url = f"{base_url}{path}"
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {"Content-Type": "application/json"} if payload is not None else {}
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        return urllib.request.urlopen(req, timeout=timeout)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ConnectionError) as e:
        print(
            f"ERROR: request to {base_url} failed: {e}\n"
            f"HINT:  The server was reachable at probe time but the generation call failed. "
            f"       Retry once, then fall back to Claude and notify the user.",
            file=sys.stderr,
        )
        sys.exit(2)


def parse_params_b(param_str: str) -> float | None:
    """Parse '125.1B' -> 125.1, '137M' -> 0.137, unknown -> None."""
    if not param_str:
        return None
    try:
        if param_str.endswith("B"):
            return float(param_str[:-1])
        if param_str.endswith("M"):
            return float(param_str[:-1]) / 1000.0
    except ValueError:
        pass
    return None


def pick_num_ctx(model_name: str, models: list[dict], override: int | None) -> int | None:
    """Return num_ctx to request. None = let Ollama use the model's default."""
    if override is not None:
        return override
    for m in models:
        if m["name"] == model_name:
            params_b = parse_params_b(m.get("details", {}).get("parameter_size", ""))
            if params_b is not None and params_b < LARGE_MODEL_THRESHOLD_B:
                return SMALL_MODEL_CTX
            return None
    # Unknown model — be conservative
    return SMALL_MODEL_CTX


def cmd_list(args):
    """List models across the fleet (or a single server if --server given)."""
    fleet = _fleet(args.server)
    if not fleet:
        _die_all_unreachable([args.server] if args.server else SERVERS)

    for base_url, models in fleet:
        print(f"\n=== {base_url} ===")
        if not models:
            print("  (no models on this server)")
            continue
        print(f"  {'NAME':<35} {'PARAMS':>10}  {'FAMILY':<18}  SIZE")
        for m in models:
            d = m.get("details", {})
            size_gb = m.get("size", 0) / 1e9
            print(
                f"  {m['name']:<35} "
                f"{d.get('parameter_size', '?'):>10}  "
                f"{d.get('family', '?'):<18}  "
                f"{size_gb:.1f} GB"
            )


def _read_prompt(args) -> str:
    if args.prompt is not None:
        return args.prompt
    if args.in_file:
        return Path(args.in_file).read_text(encoding="utf-8")
    return sys.stdin.read()


def cmd_generate(args):
    prompt = _read_prompt(args)
    if not prompt.strip():
        print("ERROR: empty prompt", file=sys.stderr)
        sys.exit(1)

    # Pick the first reachable server that has the requested model.
    base_url = _pick_server_for_model(args.model, args.server)
    # Fetch the models for that server once so pick_num_ctx doesn't re-probe.
    models = _probe(base_url) or []

    num_ctx = pick_num_ctx(args.model, models, args.num_ctx)

    options: dict = {}
    if num_ctx is not None:
        options["num_ctx"] = num_ctx
    if args.temp is not None:
        options["temperature"] = args.temp

    payload: dict = {
        "model": args.model,
        "prompt": prompt,
        "stream": args.stream,
        "keep_alive": args.keep_alive,
    }
    if options:
        payload["options"] = options

    # Log which server we ended up using (stderr so it doesn't pollute stdout).
    print(f"[using {args.model} at {base_url}]", file=sys.stderr)

    if args.stream:
        collected: list[str] = []
        with _request("/api/generate", payload, method="POST", base_url=base_url) as resp:
            for raw_line in resp:
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:
                    continue
                piece = chunk.get("response", "")
                collected.append(piece)
                # Stream to stderr so stdout stays clean for programmatic use.
                sys.stderr.write(piece)
                sys.stderr.flush()
                if chunk.get("done"):
                    break
        sys.stderr.write("\n")
        output = "".join(collected)
    else:
        with _request("/api/generate", payload, method="POST", base_url=base_url) as resp:
            data = json.loads(resp.read())
        output = data.get("response", "")

    # Final output goes to stdout (and optionally --out file).
    sys.stdout.write(output)
    if not output.endswith("\n"):
        sys.stdout.write("\n")
    if args.out_file:
        Path(args.out_file).write_text(output, encoding="utf-8")
        print(f"[wrote {len(output)} chars to {args.out_file}]", file=sys.stderr)


def cmd_embed(args):
    text = _read_prompt(args)
    base_url = _pick_server_for_model(args.model, args.server)
    payload = {"model": args.model, "prompt": text}
    print(f"[using {args.model} at {base_url}]", file=sys.stderr)
    with _request("/api/embeddings", payload, method="POST", base_url=base_url) as resp:
        data = json.loads(resp.read())
    print(json.dumps({"embedding": data.get("embedding", [])}))


def main():
    parser = argparse.ArgumentParser(
        description="Ollama helper for local Ollama servers.",
    )
    parser.add_argument(
        "--server",
        help=f"Target a specific server (e.g. http://localhost:11434). "
             f"Default: probe {SERVERS} in order.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="List models across the fleet (or a single --server).")

    g = sub.add_parser("generate", help="Text generation (completion).")
    g.add_argument("--model", required=True)
    g.add_argument("--prompt", help="Prompt text (or use --in).")
    g.add_argument("--in", dest="in_file", help="Read prompt from file.")
    g.add_argument("--out", dest="out_file", help="Write output to file.")
    g.add_argument("--num-ctx", type=int, help="Override context window (default: 64k for models <70B).")
    g.add_argument("--temp", type=float, help="Sampling temperature (default: model default).")
    g.add_argument("--no-stream", dest="stream", action="store_false", default=True)
    g.add_argument("--keep-alive", default="24h",
                   help="How long Ollama keeps model loaded after this call. "
                        "Examples: '5m' (Ollama default), '24h', '-1' (forever), '0' (unload now). "
                        "Default here: '24h' to avoid per-call model reload churn.")

    e = sub.add_parser("embed", help="Generate embeddings.")
    e.add_argument("--model", required=True)
    e.add_argument("--prompt", help="Text (or use --in).")
    e.add_argument("--in", dest="in_file", help="Read text from file (default: stdin).")

    args = parser.parse_args()

    if args.cmd == "list":
        cmd_list(args)
    elif args.cmd == "generate":
        cmd_generate(args)
    elif args.cmd == "embed":
        cmd_embed(args)


if __name__ == "__main__":
    main()
