#!/usr/bin/env python3
"""Test the Sunny voice chain with Pedalboard + SoundFile + pyloudnorm.

Usage:
    python tools/audio_test.py
    python tools/audio_test.py --input voice.wav --output sunny_voice.wav
    python tools/audio_test.py --play

If no --input is given, it generates a short vowel-like test signal so the
script runs immediately. For real tuning, use a recorded or TTS voice WAV.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from pedalboard import (
    Compressor,
    Gain,
    HighpassFilter,
    Limiter,
    PeakFilter,
    Pedalboard,
    Reverb,
)

try:
    import pyloudnorm as pyln
except ImportError:  # optional; loudness will fall back to peak normalization
    pyln = None

TARGET_LUFS = -16.0
TARGET_PEAK_DB = -1.0


def make_test_signal(sr: int = 24000, duration: float = 3.2) -> np.ndarray:
    """Generate a vowel-like signal with pauses, not a real voice."""
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    f0 = 165.0 + 5.0 * np.sin(2 * np.pi * 4.5 * t)
    phase = 2 * np.pi * np.cumsum(f0) / sr

    # Harmonic source: enough harmonics to exercise EQ and de-essing.
    source = sum(np.sin(k * phase) / k for k in range(1, 16))

    # Vowel-like formants: 700 / 1200 / 2600 Hz.
    formants = (
        0.50 * np.sin(2 * np.pi * 700 * t)
        + 0.30 * np.sin(2 * np.pi * 1200 * t)
        + 0.18 * np.sin(2 * np.pi * 2600 * t)
    )
    signal = source * (1.0 + 0.25 * formants)

    # Syllable envelope with pauses.
    env = np.zeros_like(t)
    for start, dur in ((0.10, 0.55), (0.85, 0.45), (1.45, 0.70), (2.35, 0.55)):
        mask = (t >= start) & (t < start + dur)
        env[mask] = np.sin(np.pi * (t[mask] - start) / dur) ** 1.5

    signal *= env
    signal /= max(1e-9, np.max(np.abs(signal)))
    return (0.35 * signal).astype(np.float32)


def build_chain() -> Pedalboard:
    return Pedalboard(
        [
            HighpassFilter(cutoff_frequency_hz=110),
            PeakFilter(cutoff_frequency_hz=250, gain_db=2.0, q=1.0),
            PeakFilter(cutoff_frequency_hz=3200, gain_db=1.5, q=1.0),
            Compressor(
                threshold_db=-18.0,
                ratio=3.0,
                attack_ms=10.0,
                release_ms=150.0,
            ),
            Reverb(
                room_size=0.25,
                damping=0.70,
                wet_level=0.08,
                dry_level=0.92,
                width=0.80,
            ),
            Gain(gain_db=-1.0),
        ]
    )


def process(audio: np.ndarray, sr: int) -> np.ndarray:
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)

    peak = float(np.max(np.abs(audio))) if audio.size else 0.0
    if peak > 1.0:
        audio = audio / peak * 0.9

    audio = build_chain()(audio.astype(np.float32), sr)

    if pyln is not None:
        meter = pyln.Meter(sr)
        loudness = float(meter.integrated_loudness(audio))
        if np.isfinite(loudness):
            audio = audio * (10.0 ** ((TARGET_LUFS - loudness) / 20.0))
            print(f"loudness before limiter: {loudness:.1f} LUFS -> target {TARGET_LUFS:.1f} LUFS")
        else:
            print("loudness: -inf (silence); skipping loudness normalization")
    else:
        print("pyloudnorm not installed; using peak normalization instead")

    audio = Pedalboard([Limiter(threshold_db=TARGET_PEAK_DB)])(audio, sr)
    return np.clip(audio, -1.0, 1.0).astype(np.float32)


def main() -> int:
    parser = argparse.ArgumentParser(description="Test Sunny's voice DSP chain")
    parser.add_argument("--input", type=Path, help="input WAV; omit to synthesize a test signal")
    parser.add_argument("--output", type=Path, default=Path("sunny_voice.wav"))
    parser.add_argument("--play", action="store_true", help="play the result on Windows")
    args = parser.parse_args()

    if args.input:
        if not args.input.exists():
            print(f"input not found: {args.input}", file=sys.stderr)
            return 1
        audio, sr = sf.read(str(args.input), always_2d=False)
        print(f"input: {args.input}  sr={sr}  shape={audio.shape}")
    else:
        sr = 24000
        audio = make_test_signal(sr)
        print("input: synthetic vowel-like signal (use --input voice.wav for real tuning)")

    out = process(audio, sr)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(args.output), out, sr, subtype="PCM_16")

    peak_db = 20 * np.log10(max(1e-9, float(np.max(np.abs(out)))))
    print(f"output: {args.output}  sr={sr}  duration={len(out)/sr:.2f}s  peak={peak_db:.1f} dBFS")

    if args.play:
        if sys.platform == "win32":
            import winsound

            winsound.PlaySound(str(args.output), winsound.SND_FILENAME)
        else:
            print("--play is only wired for Windows; open the WAV manually.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
