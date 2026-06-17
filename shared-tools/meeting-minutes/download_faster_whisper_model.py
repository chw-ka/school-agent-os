from __future__ import annotations

import argparse
from pathlib import Path

from huggingface_hub import snapshot_download


def main() -> int:
    ap = argparse.ArgumentParser(description="Download/complete faster-whisper model into HF cache (resume-able).")
    ap.add_argument("--model", default="large-v3", help="Model name: tiny/small/medium/large-v3")
    ap.add_argument("--repo", default=None, help="Override HF repo id (default: Systran/faster-whisper-<model>)")
    args = ap.parse_args()

    repo_id = args.repo or f"Systran/faster-whisper-{args.model}"

    # Download into the standard HF cache (resumable, supports partial downloads).
    # This is the same cache path that faster-whisper uses.
    print(f"Downloading: {repo_id}", flush=True)
    path = snapshot_download(
        repo_id=repo_id,
        resume_download=True,
        local_files_only=False,
    )
    path = Path(path)
    model_bin = path / "model.bin"
    print(f"Done. Snapshot: {path}", flush=True)
    print(f"model.bin exists: {model_bin.exists()} ({model_bin})", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

