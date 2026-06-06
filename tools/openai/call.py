#!/usr/bin/env python3
"""
tools/openai/call.py — thin OpenAI API helper, parallel to tools/ollama/call.py.

Zero dependencies (uses stdlib urllib + base64). Runs with plain python3 or via uv.

Usage:
    python3 tools/openai/call.py list
    python3 tools/openai/call.py list --filter image       # narrow to image models
    python3 tools/openai/call.py generate --model MODEL --prompt "..."
    python3 tools/openai/call.py generate --model MODEL --in prompt.txt --out result.md
    python3 tools/openai/call.py generate --model MODEL --in chapter.md --system "You are a critical editor..."
    python3 tools/openai/call.py image --model gpt-image-2 --prompt "..." --out slide.png
    python3 tools/openai/call.py image --model gpt-image-2 --in prompt.txt --out slide.png --size 1536x1024 --quality high

API key:
    Reads OPENAI_API_KEY from environment first, then from `.env` at the
    repo root. The key is never printed or logged. .env is gitignored.

When to use this vs. Ollama vs. Claude:
    Ollama (local) → routine, voluminous, mechanical (translation, summarization, cleanup)
    OpenAI (paid)  → frontier-quality second opinion, deep review, when local models
                     can't reach the bar AND the call is worth real money
    Claude Opus    → anything in the user's voice, intellectual synthesis, editorial dialogue

    Costs real money per call. The calling agent should be deliberate.
    Token usage is logged to stderr after each call so cost can be tracked.

Reasoning models (o-series, o4, o5, ...):
    Pass `--reasoning-effort low|medium|high`. Some reasoning models reject
    `--temp` or `--max-tokens`; if the API rejects a parameter, drop it and
    retry once.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

API_BASE = "https://api.openai.com/v1"
TIMEOUT_SECONDS = 600  # 10 minutes — frontier reasoning calls can be slow
REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = REPO_ROOT / ".env"


def _load_api_key() -> str:
    """Get the OpenAI API key from env or from repo .env.

    Looks for OPENAI_API_KEY (the SDK convention) but accepts case-insensitive
    variants in the .env file (e.g. openai_api_key) for ergonomics.
    Never prints the key.
    """
    # Environment variables: try the canonical name and the lowercase variant
    for name in ("OPENAI_API_KEY", "openai_api_key"):
        v = os.environ.get(name)
        if v:
            return v.strip()
    if ENV_FILE.exists():
        try:
            for raw in ENV_FILE.read_text(encoding="utf-8").splitlines():
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("export "):
                    line = line[len("export "):]
                if "=" not in line:
                    continue
                k, _, v = line.partition("=")
                if k.strip().lower() == "openai_api_key":
                    return v.strip().strip('"').strip("'")
        except OSError as e:
            print(f"ERROR: could not read {ENV_FILE}: {e}", file=sys.stderr)
            sys.exit(2)
    print(
        "ERROR: OPENAI_API_KEY not set in environment and not found in .env\n"
        f"       Checked: {ENV_FILE}\n"
        "HINT:  Either `export OPENAI_API_KEY=...` or add it to .env at the repo root.\n"
        "       Either case (OPENAI_API_KEY or openai_api_key) is accepted in .env.",
        file=sys.stderr,
    )
    sys.exit(2)


def _request(path: str, payload: dict | None = None, method: str = "GET",
             timeout: int = TIMEOUT_SECONDS):
    url = f"{API_BASE}{path}"
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {
        "Authorization": f"Bearer {_load_api_key()}",
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        return urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        # Try to surface the API's structured error message if present
        msg = body
        try:
            parsed = json.loads(body)
            if isinstance(parsed, dict) and "error" in parsed:
                err = parsed["error"]
                msg = f"{err.get('type', '?')}: {err.get('message', body)}"
        except json.JSONDecodeError:
            pass
        print(
            f"ERROR: OpenAI API HTTP {e.code} on {path}\n"
            f"       {msg[:1000]}",
            file=sys.stderr,
        )
        sys.exit(2)
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        print(
            f"ERROR: request to {url} failed: {e}\n"
            f"HINT:  Check network. If transient, retry once. Otherwise tell the user.",
            file=sys.stderr,
        )
        sys.exit(2)


def cmd_list(args):
    """List models available on the OpenAI API."""
    with _request("/models") as resp:
        data = json.loads(resp.read())
    models = sorted(data.get("data", []), key=lambda m: m.get("id", ""))
    if args.filter:
        needle = args.filter.lower()
        models = [m for m in models if needle in m.get("id", "").lower()]
    from datetime import datetime, timezone
    print(f"=== OpenAI API ({len(models)} models) ===")
    print(f"  {'NAME':<45}  {'OWNED_BY':<20}  CREATED")
    for m in models:
        mid = m.get("id", "?")
        owned = m.get("owned_by", "?")
        created = m.get("created", 0)
        try:
            ym = datetime.fromtimestamp(created, tz=timezone.utc).strftime("%Y-%m")
        except (OSError, OverflowError, ValueError):
            ym = "?"
        print(f"  {mid:<45}  {owned:<20}  {ym}")


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

    messages = []
    if args.system:
        # --system can be either inline text or a path to a file
        sys_text = args.system
        sys_path = Path(args.system)
        if sys_path.is_file():
            sys_text = sys_path.read_text(encoding="utf-8")
        messages.append({"role": "system", "content": sys_text})
    messages.append({"role": "user", "content": prompt})

    payload: dict = {
        "model": args.model,
        "messages": messages,
    }
    if args.temp is not None:
        payload["temperature"] = args.temp
    if args.max_tokens is not None:
        payload["max_completion_tokens"] = args.max_tokens
    if args.reasoning_effort:
        payload["reasoning_effort"] = args.reasoning_effort

    print(f"[using {args.model}]", file=sys.stderr)

    with _request("/chat/completions", payload, method="POST") as resp:
        data = json.loads(resp.read())

    choices = data.get("choices", [])
    if not choices:
        print(
            f"ERROR: OpenAI returned no choices.\n"
            f"       Full response: {json.dumps(data)[:500]}",
            file=sys.stderr,
        )
        sys.exit(2)
    output = choices[0].get("message", {}).get("content", "") or ""

    # Token usage to stderr — useful for tracking cost
    usage = data.get("usage", {})
    if usage:
        prompt_tok = usage.get("prompt_tokens", 0)
        completion_tok = usage.get("completion_tokens", 0)
        total_tok = usage.get("total_tokens", 0)
        # Reasoning models include reasoning_tokens inside completion_tokens_details
        details = usage.get("completion_tokens_details", {}) or {}
        reasoning_tok = details.get("reasoning_tokens", 0)
        line = f"[tokens: prompt={prompt_tok} completion={completion_tok}"
        if reasoning_tok:
            line += f" (reasoning={reasoning_tok})"
        line += f" total={total_tok}]"
        print(line, file=sys.stderr)

    finish_reason = choices[0].get("finish_reason", "")
    if finish_reason and finish_reason != "stop":
        print(f"[finish_reason: {finish_reason}]", file=sys.stderr)

    sys.stdout.write(output)
    if not output.endswith("\n"):
        sys.stdout.write("\n")
    if args.out_file:
        Path(args.out_file).write_text(output, encoding="utf-8")
        print(f"[wrote {len(output)} chars to {args.out_file}]", file=sys.stderr)


def cmd_image(args):
    """Generate an image via the /v1/images/generations endpoint and save it to --out."""
    prompt = _read_prompt(args)
    if not prompt.strip():
        print("ERROR: empty prompt", file=sys.stderr)
        sys.exit(1)

    payload: dict = {
        "model": args.model,
        "prompt": prompt,
        "n": args.n,
        "size": args.size,
        "quality": args.quality,
    }
    if args.output_format:
        payload["output_format"] = args.output_format
    if args.background:
        payload["background"] = args.background

    print(f"[using {args.model}, size={args.size}, quality={args.quality}]", file=sys.stderr)

    with _request("/images/generations", payload, method="POST") as resp:
        data = json.loads(resp.read())

    items = data.get("data", [])
    if not items:
        print(
            f"ERROR: OpenAI returned no images.\n"
            f"       Full response: {json.dumps(data)[:500]}",
            file=sys.stderr,
        )
        sys.exit(2)

    # Token-style usage on image models (gpt-image-*): { input_tokens, output_tokens, total_tokens }
    usage = data.get("usage", {})
    if usage:
        in_tok = usage.get("input_tokens", 0)
        out_tok = usage.get("output_tokens", 0)
        total_tok = usage.get("total_tokens", 0)
        details = usage.get("input_tokens_details", {}) or {}
        text_tok = details.get("text_tokens", 0)
        image_tok = details.get("image_tokens", 0)
        line = f"[tokens: input={in_tok}"
        if text_tok or image_tok:
            line += f" (text={text_tok} image={image_tok})"
        line += f" output={out_tok} total={total_tok}]"
        print(line, file=sys.stderr)

    out_path = Path(args.out_file)
    if args.n == 1:
        # Single output → write to --out directly
        targets = [(items[0], out_path)]
    else:
        # Multiple outputs → suffix with -1, -2, ...
        stem, suffix = out_path.stem, out_path.suffix or ".png"
        parent = out_path.parent
        targets = [
            (item, parent / f"{stem}-{i + 1}{suffix}")
            for i, item in enumerate(items)
        ]

    for item, path in targets:
        b64 = item.get("b64_json")
        if not b64:
            print(f"ERROR: image item missing b64_json field: {json.dumps(item)[:200]}", file=sys.stderr)
            sys.exit(2)
        path.write_bytes(base64.b64decode(b64))
        size_kb = path.stat().st_size / 1024
        print(f"[wrote {size_kb:.0f} KB to {path}]", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="OpenAI API helper, parallel to tools/ollama/call.py.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    lst = sub.add_parser("list", help="List models available on the OpenAI API.")
    lst.add_argument("--filter", help="Substring filter on model name (case-insensitive).")

    g = sub.add_parser("generate", help="Chat completion (single-turn).")
    g.add_argument("--model", required=True, help="Model id (e.g. gpt-5, gpt-4.1, o3). Run `list` to see what's available.")
    g.add_argument("--prompt", help="User prompt text (or use --in).")
    g.add_argument("--in", dest="in_file", help="Read user prompt from file.")
    g.add_argument("--out", dest="out_file", help="Write output to file (also goes to stdout).")
    g.add_argument("--system", help="System prompt text OR path to a file containing the system prompt.")
    g.add_argument("--temp", type=float, help="Sampling temperature (omit for reasoning models).")
    g.add_argument("--max-tokens", type=int, help="Max completion tokens (max_completion_tokens).")
    g.add_argument("--reasoning-effort", choices=["low", "medium", "high"], help="For o-series / reasoning models only.")

    i = sub.add_parser("image", help="Generate an image (gpt-image-* models).")
    i.add_argument("--model", required=True, help="Image model id (e.g. gpt-image-2, gpt-image-1.5). Run `list --filter image`.")
    i.add_argument("--prompt", help="Prompt text (or use --in).")
    i.add_argument("--in", dest="in_file", help="Read prompt from file.")
    i.add_argument("--out", dest="out_file", required=True, help="Output path (e.g. tmp/slide.png). When --n > 1, files get -1, -2 suffixes.")
    i.add_argument("--size", default="1024x1024", help="Image size: 1024x1024 | 1024x1536 | 1536x1024 | auto (default: 1024x1024).")
    i.add_argument("--quality", default="high", choices=["low", "medium", "high", "auto"], help="Render quality (default: high).")
    i.add_argument("--n", type=int, default=1, help="Number of images to generate (default: 1).")
    i.add_argument("--output-format", choices=["png", "jpeg", "webp"], help="Output file format (model default if omitted).")
    i.add_argument("--background", choices=["transparent", "opaque", "auto"], help="Background handling (transparent works for png/webp).")

    args = parser.parse_args()

    if args.cmd == "list":
        cmd_list(args)
    elif args.cmd == "generate":
        cmd_generate(args)
    elif args.cmd == "image":
        cmd_image(args)


if __name__ == "__main__":
    main()
