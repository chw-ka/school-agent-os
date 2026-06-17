import argparse
from dataclasses import dataclass
from pathlib import Path

from faster_whisper import WhisperModel


@dataclass(frozen=True)
class SegmentRow:
    start: float
    end: float
    text: str


def format_ts(sec: float) -> str:
    sec = max(0.0, float(sec))
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"


def transcribe_one_streaming(
    model: WhisperModel,
    audio_path: Path,
    language: str | None,
) -> tuple[Path, int]:
    segments, _info = model.transcribe(
        str(audio_path),
        language=language,
        vad_filter=True,
    )
    out_path = audio_path.with_suffix("").with_suffix(".transcript.txt")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    n_written = 0
    with out_path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(f"# {audio_path.name}\n\n")
        f.flush()

        for i, seg in enumerate(segments, start=1):
            text = (seg.text or "").strip()
            if not text:
                continue
            row = SegmentRow(start=float(seg.start), end=float(seg.end), text=text)
            f.write(f"[{format_ts(row.start)}–{format_ts(row.end)}] {row.text}\n")
            n_written += 1
            if n_written % 50 == 0:
                f.flush()
                print(f"{audio_path.name}: wrote {n_written} segments...")

        f.write("\n")
        f.flush()

    return out_path, n_written


def main() -> int:
    ap = argparse.ArgumentParser(description="Transcribe audio files using faster-whisper.")
    ap.add_argument("audio", nargs="+", type=Path, help="Audio file path(s) (m4a/wav/mp3/...)")
    ap.add_argument("--model", default="small", help="Whisper model size: tiny/base/small/medium/large-v3")
    ap.add_argument(
        "--model-path",
        type=Path,
        default=None,
        help="Optional local path to a cached faster-whisper model (ctranslate2). If not set, will try to auto-detect from HF cache.",
    )
    ap.add_argument("--device", default="cpu", help="Device: cpu/cuda")
    ap.add_argument("--compute-type", default="int8", help="Compute type, e.g. int8/int8_float16/float16")
    ap.add_argument("--language", default="zh", help="Language code, e.g. zh/en; use 'auto' to detect")
    ap.add_argument("--out-dir", type=Path, required=True, help="Output directory")
    args = ap.parse_args()

    language = None if args.language == "auto" else args.language
    model_src: str | Path = args.model
    if args.model_path is not None:
        model_src = args.model_path
    else:
        # Try to avoid network by using the local HF cache if present.
        # Example: %USERPROFILE%\.cache\huggingface\hub\models--Systran--faster-whisper-large-v3\snapshots\<hash>\
        cache_root = Path.home() / ".cache" / "huggingface" / "hub"
        model_dir = cache_root / f"models--Systran--faster-whisper-{args.model}"
        snapshots = model_dir / "snapshots"
        if snapshots.exists():
            snap_candidates = sorted([p for p in snapshots.iterdir() if p.is_dir()], key=lambda p: p.name, reverse=True)
            if snap_candidates:
                model_src = snap_candidates[0]
    print(f"Loading model from: {model_src}", flush=True)
    model = WhisperModel(str(model_src), device=args.device, compute_type=args.compute_type)

    for a in args.audio:
        out = args.out_dir / f"{a.stem}.transcript.txt"
        print(
            f"Starting: {a} -> {out} (model={args.model}, lang={args.language}, device={args.device}, compute={args.compute_type})",
            flush=True,
        )
        out.parent.mkdir(parents=True, exist_ok=True)
        # Stream to the final output path (avoid losing hours of work).
        tmp_audio_path = out.with_suffix("").with_suffix(a.suffix)
        # We don't copy audio; just pass original path and write to `out`.
        segments, _info = model.transcribe(
            str(a),
            language=language,
            vad_filter=True,
        )
        n_written = 0
        with out.open("w", encoding="utf-8", newline="\n") as f:
            f.write(f"# {a.name}\n\n")
            f.flush()
            for seg in segments:
                text = (seg.text or "").strip()
                if not text:
                    continue
                f.write(f"[{format_ts(float(seg.start))}–{format_ts(float(seg.end))}] {text}\n")
                n_written += 1
                if n_written % 50 == 0:
                    f.flush()
                    print(f"{a.name}: wrote {n_written} segments...", flush=True)
            f.write("\n")
            f.flush()
        print(f"Done: {a.name} ({n_written} segments)", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

