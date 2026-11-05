#!/usr/bin/env python3
r"""Synthesize a Sunny test line with edge-tts.

Run from the VS Code terminal:
    .\.venv\Scripts\python.exe tools\tts_edge.py
    .\.venv\Scripts\python.exe tools\tts_edge.py --text "..." --voice zh-CN-YunxiNeural
    .\.venv\Scripts\python.exe tools\tts_edge.py --play
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a Sunny voice line with edge-tts")
    parser.add_argument("--text", default="我在。你慢慢说。今天是不是发生了什么事？")
    parser.add_argument("--voice", default="zh-CN-XiaoxiaoNeural")
    parser.add_argument("--out", type=Path, default=Path("sunny.mp3"))
    parser.add_argument("--rate", default="-5%", help="e.g. -5%% or +0%%")
    parser.add_argument("--pitch", default="-2Hz", help="e.g. -2Hz or +0Hz")
    parser.add_argument("--play", action="store_true", help="open the file on Windows")
    return parser.parse_args()


async def synthesize(text: str, voice: str, out: Path, rate: str, pitch: str) -> None:
    import edge_tts

    tts = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await tts.save(str(out))


def main() -> int:
    args = parse_args()

    try:
        import edge_tts  # noqa: F401
    except ImportError:
        print("edge-tts is not installed in this Python.", file=sys.stderr)
        print(f"Python: {sys.executable}", file=sys.stderr)
        print(f"Install: {sys.executable} -m pip install edge-tts", file=sys.stderr)
        return 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    asyncio.run(synthesize(args.text, args.voice, args.out, args.rate, args.pitch))

    path = args.out.resolve()
    print(f"wrote: {path}")
    print(f"voice: {args.voice}  rate: {args.rate}  pitch: {args.pitch}")
    print(f"python: {sys.executable}")

    if args.play:
        if sys.platform == "win32":
            os.startfile(path)
        else:
            print("Open the file manually; --play is wired for Windows only.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
