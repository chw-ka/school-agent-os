from __future__ import annotations

from pathlib import Path


def main() -> int:
    root = Path.home() / ".cache" / "huggingface" / "hub"
    models = ["tiny", "small", "large-v3"]
    for m in models:
        snapshots = root / f"models--Systran--faster-whisper-{m}" / "snapshots"
        if not snapshots.exists():
            print(f"{m}: no snapshots")
            continue
        snap_dirs = sorted([p for p in snapshots.iterdir() if p.is_dir()], key=lambda p: p.name, reverse=True)
        ok = next((s for s in snap_dirs if (s / "model.bin").exists()), None)
        if ok is None:
            print(f"{m}: missing model.bin (snapshots={len(snap_dirs)})")
        else:
            print(f"{m}: OK (model.bin) snapshot={ok.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

