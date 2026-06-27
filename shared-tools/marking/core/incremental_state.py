import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


STATE_PATH = Path(".cache") / "incremental_state.json"


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _to_iso(dt_like: Any) -> Optional[str]:
    if dt_like is None:
        return None
    if isinstance(dt_like, str):
        return dt_like.replace("Z", "+00:00")
    if isinstance(dt_like, datetime):
        if dt_like.tzinfo is None:
            dt_like = dt_like.replace(tzinfo=timezone.utc)
        return dt_like.astimezone(timezone.utc).isoformat()
    return str(dt_like)


def _parse_iso(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def submission_key(course_id: str, assignment_id: str, submission_id: str) -> str:
    return f"{course_id}::{assignment_id}::{submission_id}"


@dataclass
class SubmissionState:
    last_submitted_date_time: Optional[str] = None
    last_modified_date_time: Optional[str] = None
    latest_filepath: Optional[str] = None
    last_submitted_marks: Optional[float] = None
    last_submitted_comments: Optional[str] = None


def load_state(path: Path = STATE_PATH) -> Dict[str, Any]:
    if not path.exists():
        return {"version": 1, "submissions": {}}
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if "submissions" not in data:
        data["submissions"] = {}
    if "version" not in data:
        data["version"] = 1
    return data


def save_state(state: Dict[str, Any], path: Path = STATE_PATH) -> None:
    _ensure_parent(path)
    with path.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def get_submission_state(
    state: Dict[str, Any], course_id: str, assignment_id: str, submission_id: str
) -> SubmissionState:
    key = submission_key(course_id, assignment_id, submission_id)
    raw = state.get("submissions", {}).get(key, {}) or {}
    return SubmissionState(
        last_submitted_date_time=raw.get("last_submitted_date_time"),
        last_modified_date_time=raw.get("last_modified_date_time"),
        latest_filepath=raw.get("latest_filepath"),
        last_submitted_marks=raw.get("last_submitted_marks"),
        last_submitted_comments=raw.get("last_submitted_comments"),
    )


def set_download_info(
    state: Dict[str, Any],
    course_id: str,
    assignment_id: str,
    submission_id: str,
    submitted_date_time: Any,
    last_modified_date_time: Any,
    latest_filepath: Optional[str],
) -> None:
    key = submission_key(course_id, assignment_id, submission_id)
    state.setdefault("submissions", {})
    existing = state["submissions"].get(key, {}) or {}
    existing["last_submitted_date_time"] = _to_iso(submitted_date_time)
    existing["last_modified_date_time"] = _to_iso(last_modified_date_time)
    if latest_filepath:
        existing["latest_filepath"] = latest_filepath
    state["submissions"][key] = existing


def needs_redownload(
    state: Dict[str, Any],
    course_id: str,
    assignment_id: str,
    submission_id: str,
    remote_submitted_date_time: Any,
) -> bool:
    remote_iso = _to_iso(remote_submitted_date_time)
    if not remote_iso:
        return False
    remote_dt = _parse_iso(remote_iso)
    if remote_dt is None:
        return False
    local = get_submission_state(state, course_id, assignment_id, submission_id)
    local_dt = _parse_iso(local.last_submitted_date_time)
    if local_dt is None:
        return True
    return remote_dt > local_dt


def mark_submitted(
    state: Dict[str, Any],
    course_id: str,
    assignment_id: str,
    submission_id: str,
    marks: Any,
    comments: Any,
) -> None:
    key = submission_key(course_id, assignment_id, submission_id)
    state.setdefault("submissions", {})
    existing = state["submissions"].get(key, {}) or {}
    try:
        existing["last_submitted_marks"] = float(marks)
    except Exception:
        existing["last_submitted_marks"] = None
    existing["last_submitted_comments"] = "" if comments is None else str(comments)
    state["submissions"][key] = existing
