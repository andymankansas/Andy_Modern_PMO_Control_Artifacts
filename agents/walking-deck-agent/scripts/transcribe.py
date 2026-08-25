"""Optional: transcribe a meeting recording locally with faster-whisper.

This is an OPTIONAL capability. Install the extra dependency first:
    pip install -r requirements-transcribe.txt

Usage:
    python scripts/transcribe.py "path/to/recording.mp4" [--model small.en] [--out-dir output]

Writes a timestamped transcript and a continuous plain-text transcript next to
the recording (or into --out-dir). No cloud calls; runs on CPU.
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path


def _ts(seconds: float) -> str:
    seconds = int(seconds)
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Transcribe a recording with faster-whisper (offline, CPU).")
    parser.add_argument("recording", help="Path to .mp4/.wav/.m4a recording")
    parser.add_argument("--model", default="small.en", help="faster-whisper model (default: small.en)")
    parser.add_argument("--out-dir", default=None, help="Output folder (default: next to the recording)")
    args = parser.parse_args()

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("faster-whisper is not installed. Run: pip install -r requirements-transcribe.txt")
        return 2

    src = Path(args.recording)
    if not src.exists():
        print(f"Not found: {src}")
        return 2
    out_dir = Path(args.out_dir) if args.out_dir else src.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = src.stem
    out_txt = out_dir / f"{stem}_Transcript.txt"
    out_plain = out_dir / f"{stem}_Transcript_plain.txt"

    start = time.time()
    print(f"Loading model '{args.model}' (cpu/int8)...", flush=True)
    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    print("Transcribing...", flush=True)
    segments, info = model.transcribe(str(src), vad_filter=True,
                                      vad_parameters=dict(min_silence_duration_ms=500), beam_size=5)

    lines, plain = [], []
    for seg in segments:
        text = seg.text.strip()
        if not text:
            continue
        lines.append(f"[{_ts(seg.start)}] {text}")
        plain.append(text)

    header = (
        f"Transcript: {src.name}\n"
        f"Duration: {_ts(info.duration)}  |  Model: {args.model}  |  Language: {info.language}\n"
        + "=" * 70 + "\n\n"
    )
    out_txt.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")
    out_plain.write_text(" ".join(plain) + "\n", encoding="utf-8")
    print(f"Done in {round((time.time() - start) / 60, 1)} min | segments: {len(lines)}")
    print(f"Timestamped: {out_txt}")
    print(f"Plain:       {out_plain}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
