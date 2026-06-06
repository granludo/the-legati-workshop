"""tools/wiki/chunk.py — split long markdown into 16k-context-safe chunks for Ollama.

Per `feedback_ollama_context_under_16k.md`: total context ≤ 16k tokens. Reserve
~1.5k for prompt scaffolding and ~1k for JSON output → working *input* budget
of ~13k tokens. Conservative for prose: 3.5 chars/token, so ~45 KB of plain
markdown per chunk. We aim lower (~10k tokens, ~35 KB) to stay safely below
the cliff.

Splitting strategy, in order:
  1. By markdown H2 headings (best — preserves logical sections).
  2. By paragraph boundaries (\n\n) if no usable H2 split exists.
  3. By sentence (last resort; sentence-per-line heuristic).
"""
from __future__ import annotations
import re
from typing import Iterable

CHARS_PER_TOKEN = 3.5
DEFAULT_BUDGET_TOKENS = 10000


def estimate_tokens(text: str) -> int:
    return int(len(text) / CHARS_PER_TOKEN) + 1


def _greedy_combine(parts: Iterable[str], budget: int, sep: str) -> list[str]:
    chunks: list[str] = []
    current = ""
    for p in parts:
        if not p:
            continue
        candidate = current + sep + p if current else p
        if estimate_tokens(candidate) > budget and current:
            chunks.append(current)
            current = p
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


def chunk_markdown(text: str, budget_tokens: int = DEFAULT_BUDGET_TOKENS) -> list[str]:
    """Split `text` into chunks each within `budget_tokens`."""
    if estimate_tokens(text) <= budget_tokens:
        return [text]

    # Tier 1: H2 splits.
    h2_parts = re.split(r"(?m)(?=^## )", text)
    if len(h2_parts) > 1:
        chunks = _greedy_combine(h2_parts, budget_tokens, sep="")
        if all(estimate_tokens(c) <= budget_tokens for c in chunks):
            return chunks

    # Tier 2: paragraph splits.
    para_parts = re.split(r"\n\n+", text)
    chunks = _greedy_combine(para_parts, budget_tokens, sep="\n\n")
    if all(estimate_tokens(c) <= budget_tokens for c in chunks):
        return chunks

    # Tier 3: sentence-ish splits (last-resort).
    sent_parts = re.split(r"(?<=[.!?])\s+", text)
    return _greedy_combine(sent_parts, budget_tokens, sep=" ")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("usage: python3 chunk.py <file>")
        sys.exit(1)
    text = open(sys.argv[1]).read()
    chunks = chunk_markdown(text)
    print(f"input:  {estimate_tokens(text)} tokens, {len(text)} chars")
    print(f"output: {len(chunks)} chunks")
    for i, c in enumerate(chunks):
        print(f"  chunk {i}: {estimate_tokens(c)} tokens, {len(c)} chars")
