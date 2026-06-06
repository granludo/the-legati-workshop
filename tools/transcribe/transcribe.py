"""Transcribe mp4 files using mlx-whisper large-v3 on Apple Silicon.

Usage:
    uv run transcribe.py --lang ca file1.mp4 file2.mp4 ...
    uv run transcribe.py --lang es file1.mp4 file2.mp4 ...

Writes <file>.srt and <file>.txt next to each input. Skips files whose
outputs already exist so the script is safe to re-run.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import mlx_whisper

MODEL = "mlx-community/whisper-large-v3-mlx"


def format_timestamp(seconds: float) -> str:
    ms = round(seconds * 1000)
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(segments, path: Path) -> None:
    lines = []
    for i, seg in enumerate(segments, start=1):
        start = format_timestamp(seg["start"])
        end = format_timestamp(seg["end"])
        text = seg["text"].strip()
        lines.append(f"{i}\n{start} --> {end}\n{text}\n")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_txt(segments, path: Path) -> None:
    text = "\n".join(seg["text"].strip() for seg in segments)
    path.write_text(text + "\n", encoding="utf-8")


def transcribe_one(media: Path, language: str) -> None:
    srt_path = media.with_suffix(".srt")
    txt_path = media.with_suffix(".txt")
    if srt_path.exists() and txt_path.exists():
        print(f"  [skip] already transcribed: {media.name}")
        return

    start = time.time()
    result = mlx_whisper.transcribe(
        str(media),
        path_or_hf_repo=MODEL,
        language=language,
        verbose=False,
        word_timestamps=False,
    )
    elapsed = time.time() - start

    segments = result["segments"]
    write_srt(segments, srt_path)
    write_txt(segments, txt_path)
    print(f"  [done] {media.name}  ({elapsed:.1f}s, {len(segments)} segments)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lang", required=True, choices=["ca", "es", "en"])
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args()

    missing = [f for f in args.files if not f.exists()]
    if missing:
        for f in missing:
            print(f"ERROR: missing file: {f}", file=sys.stderr)
        return 1

    print(f"Model: {MODEL}")
    print(f"Language: {args.lang}")
    print(f"Files: {len(args.files)}")
    print()

    total_start = time.time()
    for i, media in enumerate(args.files, start=1):
        print(f"[{i}/{len(args.files)}] {media.name}")
        try:
            transcribe_one(media, args.lang)
        except Exception as e:
            print(f"  [error] {e}", file=sys.stderr)
    print(f"\nTotal: {time.time() - total_start:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
