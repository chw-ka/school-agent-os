"""Discover and launch student .py games from a folder (tkinter / stdlib)."""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path

# Filename like: 3D01 Name (中文)_uuid_uuid_uuid_0.py
_UUID_SPLIT = re.compile(r"_[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-", re.MULTILINE)


def default_games_root() -> Path:
    """Folder 【Python與人工智能】第五章　任務三 next to project root."""
    here = Path(__file__).resolve().parent
    return here.parent / "【Python與人工智能】第五章　任務三"


def parse_title(stem: str) -> str:
    """Human label from file stem (strip assignment UUIDs)."""
    parts = _UUID_SPLIT.split(stem, maxsplit=1)
    return parts[0].strip() if parts else stem


def discover_games(root: Path | None = None) -> list[dict]:
    """
    Return sorted list of { id, title, relpath, filename }.
    relpath is posix relative to root.
    """
    root = (root or default_games_root()).resolve()
    if not root.is_dir():
        return []

    out: list[dict] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() != ".py":
            continue
        rel = path.relative_to(root)
        rel_posix = rel.as_posix()
        gid = hashlib.sha256(rel_posix.encode("utf-8")).hexdigest()[:16]
        stem = path.stem
        title = parse_title(stem)
        out.append(
            {
                "id": gid,
                "title": title,
                "relpath": rel_posix,
                "filename": path.name,
            }
        )
    out.sort(key=lambda x: (x["title"].lower(), x["filename"]))
    return out


def is_safe_under(root: Path, candidate: Path) -> bool:
    root = root.resolve()
    candidate = candidate.resolve()
    try:
        candidate.relative_to(root)
        return True
    except ValueError:
        return False


def launch_game(root: Path, relpath: str) -> subprocess.Popen:
    """Run python game_path; cwd = game file directory."""
    root = root.resolve()
    if ".." in relpath or relpath.startswith(("/", "\\")):
        raise ValueError("Invalid path")
    game_path = (root / relpath).resolve()
    if not game_path.is_file() or game_path.suffix.lower() != ".py":
        raise ValueError("Not a Python file")
    if not is_safe_under(root, game_path):
        raise ValueError("Path outside games folder")

    cwd = game_path.parent
    return subprocess.Popen([sys.executable, str(game_path)], cwd=str(cwd))
