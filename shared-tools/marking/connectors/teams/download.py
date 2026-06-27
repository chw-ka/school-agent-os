"""
Download assignment submissions from MS Teams.

Run from a subject's marking directory, e.g. Subjects/S3-CMP/marking/:
    python ../../../shared-tools/marking/connectors/teams/download.py --session 25_26_pai

Files are saved as  attachments/<assignment>/<class><number>_<original_filename>
A manifest.json sidecar is written per assignment with full submission metadata.
"""

import asyncio
import json
import re
import sys
import time
import argparse
from datetime import datetime, timezone
from os import makedirs, path, stat
from pathlib import Path

_MARKING_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_MARKING_ROOT))

from connectors.teams.mygraph.client import MSGraphClient
from core.incremental_state import (
    load_state, save_state, needs_redownload, set_download_info
)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

client = MSGraphClient(is_application=True)

MAX_RETRIES = 3
RETRY_DELAY = 5
BATCH_SIZE = 10
MAX_CONCURRENT_DOWNLOADS = 3
CLIENT_RENEWAL_THRESHOLD = 50
RATE_LIMIT_DELAY = 2

INVALID_WIN_CHARS = re.compile(r'[<>:"/\\|?*]')


def safe_foldername(name: str) -> str:
    return INVALID_WIN_CHARS.sub("_", name).strip().rstrip(".")


def load_config(session_name: str):
    with open("platform.json", encoding="utf-8") as f:
        platform = json.load(f)
    session_path = Path("sessions") / f"{session_name}.session.json"
    with session_path.open(encoding="utf-8") as f:
        session = json.load(f)
    return platform, session


def load_manifest(assignment_folder: Path) -> dict:
    manifest_path = assignment_folder / "manifest.json"
    if manifest_path.exists():
        with manifest_path.open(encoding="utf-8") as f:
            return json.load(f)
    return {"submissions": []}


def save_manifest(assignment_folder: Path, manifest: dict) -> None:
    manifest_path = assignment_folder / "manifest.json"
    manifest["downloaded_at"] = datetime.now(tz=timezone.utc).isoformat()
    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


def upsert_submission_manifest(manifest: dict, submission_entry: dict) -> None:
    """Insert or update a submission entry in the manifest by submission_id."""
    sub_id = submission_entry["submission_id"]
    for i, s in enumerate(manifest["submissions"]):
        if s["submission_id"] == sub_id:
            manifest["submissions"][i] = submission_entry
            return
    manifest["submissions"].append(submission_entry)


def bootstrap_state_from_manifests(state):
    attachments_dir = Path("attachments")
    if not attachments_dir.exists():
        print("ℹ️ No attachments/ folder found; skip bootstrap.")
        return 0
    updated = 0
    for manifest_path in attachments_dir.rglob("manifest.json"):
        try:
            with manifest_path.open(encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue
        for sub in data.get("submissions", []):
            sub_id = sub.get("submission_id")
            course_id = sub.get("course_id")
            assignment_id = sub.get("assignment_id")
            if not all([sub_id, course_id, assignment_id]):
                continue
            files = sub.get("files", [])
            latest_path = None
            if files:
                latest_path = str(manifest_path.parent / files[-1]["stored_filename"])
            set_download_info(
                state, course_id, assignment_id, sub_id,
                sub.get("submitted_at"), sub.get("submitted_at"), latest_path
            )
            updated += 1
    save_state(state)
    print(f"🧩 Bootstrapped incremental state from manifests: {updated} submissions")
    return updated


def _marksheet_mtime_by_assignment() -> dict:
    m = {}
    marks_dir = Path("marksheets")
    if not marks_dir.exists():
        return m
    for p in marks_dir.glob("marksheets_*.csv"):
        assignment_part = p.name[len("marksheets_"):-len(".csv")]
        try:
            m[assignment_part] = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
        except Exception:
            continue
    return m


def _results_csv_mtime() -> datetime | None:
    p = Path("results.csv")
    if not p.exists():
        return None
    try:
        return datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
    except Exception:
        return None


def _to_dt_utc(dt_like):
    if dt_like is None:
        return None
    if isinstance(dt_like, datetime):
        return dt_like.replace(tzinfo=timezone.utc) if dt_like.tzinfo is None else dt_like.astimezone(timezone.utc)
    if isinstance(dt_like, str):
        try:
            return datetime.fromisoformat(dt_like.replace("Z", "+00:00")).astimezone(timezone.utc)
        except Exception:
            return None
    return None


def _is_resubmitted_status(status) -> bool:
    s = str(status or "").lower()
    return "submitted" in s and "returned" not in s


async def get_all_members(course_id):
    members = await client.get_group_members(course_id)
    return [
        {
            "id": member.id,
            "display_name": member.display_name,
            "class": member.display_name[0:2],
            "classnumber": member.display_name[2:4],
        }
        for member in members
    ]


async def get_all_assignments(course_id):
    assignments = await client.get_assignments(course_id)
    return [{"id": a.id, "display_name": a.display_name} for a in assignments]


async def get_all_submissions(course_id, assignment_id):
    submissions = await client.get_submissions(course_id, assignment_id)
    return [
        {
            "id": s.id,
            "recipient": s.recipient,
            "submitted_resources": s.submitted_resources,
            "course_id": course_id,
            "assignment_id": assignment_id,
            "submitted_date_time": getattr(s, "submitted_date_time", None),
            "last_modified_date_time": getattr(s, "last_modified_date_time", None),
            "status": getattr(s, "status", None),
        }
        for s in submissions
    ]


def should_redownload_file(file_path, submission_datetime):
    if not path.exists(file_path):
        return True
    if submission_datetime is None:
        return False
    try:
        file_mtime = stat(file_path).st_mtime
        file_dt = datetime.fromtimestamp(file_mtime)
        if isinstance(submission_datetime, str):
            submission_datetime = datetime.fromisoformat(submission_datetime.replace("Z", "+00:00"))
        return submission_datetime.replace(tzinfo=None) > file_dt
    except Exception as e:
        print(f"Error comparing timestamps for {file_path}: {e}")
        return False


async def download_file(file_url, save_to, timeout=30):
    for attempt in range(MAX_RETRIES):
        try:
            await asyncio.wait_for(client.download_file(file_url, save_to), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            print(f"⏰ Timeout downloading (attempt {attempt + 1}/{MAX_RETRIES})")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY * (attempt + 1))
        except Exception as e:
            print(f"❌ Error downloading (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY * (attempt + 1))
    print(f"💥 Failed to download after {MAX_RETRIES} attempts")
    return False


async def download_submission_resources(submission):
    """Download files for one submission. Returns list of file-info dicts, or None on failure."""
    submitted_resources = submission.get("submitted_resources")

    if not submitted_resources:
        student_name = submission.get("recipient", {}).get("display_name", "Unknown")
        print(f"⚠️ No submitted_resources for {student_name}, trying alternative endpoint...")
        try:
            alt = await client.get_submitted_resources(
                submission["course_id"], submission["assignment_id"], submission["id"]
            )
            if alt:
                submitted_resources = alt
            else:
                print(f"⚠️ No resources found via alternative endpoint for {student_name}")
                return None
        except Exception as e:
            print(f"❌ Error fetching alternative resources for {student_name}: {e}")
            return None

    student_prefix = submission["recipient"]["class"] + submission["recipient"]["classnumber"]
    assignment_folder = Path("attachments") / safe_foldername(submission["assignment"]["display_name"])
    assignment_folder.mkdir(parents=True, exist_ok=True)

    file_infos = []
    for i, resource in enumerate(submitted_resources):
        resource_obj = None
        if hasattr(resource, "resource"):
            resource_obj = resource.resource
        elif hasattr(resource, "file_url"):
            resource_obj = resource
        else:
            print(f"⚠️ Resource {i} has unexpected structure")
            continue

        if not hasattr(resource_obj, "file_url") or resource_obj.file_url is None:
            print(f"⚠️ Resource {i} has no file_url — likely a link submission")
            continue

        original_filename = resource_obj.display_name
        stored_filename = f"{student_prefix}_{original_filename}"
        save_to = str(assignment_folder / stored_filename)

        file_infos.append({
            "file_url": resource_obj.file_url,
            "save_to": save_to,
            "original_filename": original_filename,
            "stored_filename": stored_filename,
            "file_index": i,
        })

    if not file_infos:
        print(f"⚠️ No downloadable resources for {student_prefix} in {submission['assignment']['display_name']}")
        return None

    submission_datetime = submission.get("submitted_date_time") or submission.get("last_modified_date_time")
    download_tasks = [
        download_file(fi["file_url"], fi["save_to"])
        for fi in file_infos
        if should_redownload_file(fi["save_to"], submission_datetime)
    ]

    if download_tasks:
        max_concurrent = min(MAX_CONCURRENT_DOWNLOADS, len(download_tasks))
        successful = 0
        for i in range(0, len(download_tasks), max_concurrent):
            results = await asyncio.gather(*download_tasks[i:i + max_concurrent], return_exceptions=True)
            successful += sum(1 for r in results if r is True)
        print(f"✅ Downloaded {successful}/{len(download_tasks)} files for {student_prefix}")
    else:
        print(f"ℹ️ All files up to date for {student_prefix}")

    return file_infos


async def main():
    parser = argparse.ArgumentParser(description="Download assignment submissions from Teams")
    parser.add_argument("--session", required=True, help="Session name (e.g. 25_26_pai)")
    parser.add_argument("--only-updated", action="store_true")
    parser.add_argument("--write-updated-list", action="store_true")
    parser.add_argument("--bootstrap-state-from-manifests", action="store_true")
    parser.add_argument("--since-marksheets", action="store_true")
    parser.add_argument("--since-results", action="store_true")
    parser.add_argument("--only-reassigned", action="store_true")
    parser.add_argument("--only-submitted", action="store_true")
    parser.add_argument("--min-resource-count", type=int, default=None)
    args = parser.parse_args()

    platform, session = load_config(args.session)
    courses = platform["courses"]
    state = load_state()

    if args.bootstrap_state_from_manifests:
        bootstrap_state_from_manifests(state)

    marksheet_mtime = _marksheet_mtime_by_assignment() if args.since_marksheets else {}
    results_cutoff = _results_csv_mtime() if args.since_results else None

    members = []
    for course in courses:
        members += await get_all_members(course["id"])
    print(f"{len(members)} members loaded")
    members_dict = {m["id"]: m for m in members}

    available_assignments = [a["display_name"] for a in session["assignments"]]
    assignments = []
    for course in courses:
        ms_assignments = await get_all_assignments(course["id"])
        assignments += [
            {"id": a["id"], "course_id": course["id"], "display_name": a["display_name"]}
            for a in ms_assignments
            if a["display_name"] in available_assignments
        ]
    print(f"{len(assignments)} assignments loaded")

    submissions = []
    for assignment in assignments:
        ms_subs = await get_all_submissions(assignment["course_id"], assignment["id"])
        for s in ms_subs:
            s["recipient"] = members_dict[s["recipient"].user_id]
            s["assignment"] = assignment
        submissions += ms_subs
    print(f"{len(submissions)} submissions loaded")

    updated_submissions = []
    if args.only_updated:
        for submission in submissions:
            if args.only_submitted:
                if _is_resubmitted_status(submission.get("status")):
                    updated_submissions.append(submission)
                continue
            if args.min_resource_count is not None:
                resources = submission.get("submitted_resources")
                if resources and len(resources) >= args.min_resource_count:
                    updated_submissions.append(submission)
                continue
            if args.only_reassigned:
                if str(submission.get("status") or "").lower() == "reassigned":
                    updated_submissions.append(submission)
                continue
            submitted_dt = _to_dt_utc(submission.get("submitted_date_time"))
            if args.since_results:
                if results_cutoff is None or (submitted_dt and submitted_dt > results_cutoff):
                    updated_submissions.append(submission)
                continue
            if args.since_marksheets:
                cutoff = marksheet_mtime.get(submission["assignment"]["display_name"])
                if cutoff is None or (submitted_dt and submitted_dt > cutoff):
                    updated_submissions.append(submission)
                continue
            if needs_redownload(
                state,
                submission["assignment"]["course_id"],
                submission["assignment"]["id"],
                submission["id"],
                submission.get("submitted_date_time"),
            ):
                updated_submissions.append(submission)
        print(f"🧩 only-updated: {len(updated_submissions)} / {len(submissions)} submissions need download")
        submissions = updated_submissions

    # Accumulate manifest data per assignment folder.
    manifests: dict[str, dict] = {}

    counter = 1
    failed_submissions = []
    print(f"📥 Downloading {len(submissions)} submissions in batches of {BATCH_SIZE}")

    for i in range(0, len(submissions), BATCH_SIZE):
        batch = submissions[i:i + BATCH_SIZE]
        print(f"\n🔄 Batch {i // BATCH_SIZE + 1}/{(len(submissions) + BATCH_SIZE - 1) // BATCH_SIZE}")

        download_tasks = []
        for submission in batch:
            print(f"[{counter}/{len(submissions)}] ", end="")
            download_tasks.append((submission, download_submission_resources(submission)))
            counter += 1

        batch_timeout = 300
        try:
            coros = [coro for _, coro in download_tasks]
            results = await asyncio.wait_for(
                asyncio.gather(*coros, return_exceptions=True), timeout=batch_timeout
            )
        except asyncio.TimeoutError:
            print(f"⏰ Batch timeout after {batch_timeout}s")
            results = [None for _ in download_tasks]

        for (submission, _), file_infos in zip(download_tasks, results):
            if isinstance(file_infos, Exception):
                file_infos = None

            sub_id = submission["id"]
            course_id = submission["assignment"]["course_id"]
            assignment_id = submission["assignment"]["id"]
            assignment_name = submission["assignment"]["display_name"]
            folder_name = safe_foldername(assignment_name)

            latest_filepath = None
            manifest_files = []

            if file_infos:
                latest_filepath = file_infos[-1]["save_to"]
                manifest_files = [
                    {
                        "original_filename": fi["original_filename"],
                        "stored_filename": fi["stored_filename"],
                        "file_index": fi["file_index"],
                    }
                    for fi in file_infos
                ]
            else:
                failed_submissions.append(sub_id)

            set_download_info(
                state, course_id, assignment_id, sub_id,
                submission.get("submitted_date_time"),
                submission.get("last_modified_date_time"),
                latest_filepath,
            )

            # Build manifest entry.
            recipient = submission["recipient"]
            sub_entry = {
                "submission_id": sub_id,
                "course_id": course_id,
                "assignment_id": assignment_id,
                "student": recipient["display_name"],
                "class": recipient["class"],
                "class_number": recipient["classnumber"],
                "submitted_at": str(submission.get("submitted_date_time") or ""),
                "status": str(submission.get("status") or ""),
                "files": manifest_files,
            }
            if folder_name not in manifests:
                manifests[folder_name] = load_manifest(Path("attachments") / folder_name)
                manifests[folder_name].setdefault("assignment", assignment_name)
                manifests[folder_name].setdefault("platform", "teams")
            upsert_submission_manifest(manifests[folder_name], sub_entry)

        save_state(state)

        if i + BATCH_SIZE < len(submissions):
            print(f"⏳ Waiting {RATE_LIMIT_DELAY}s...")
            await asyncio.sleep(RATE_LIMIT_DELAY)

    # Write manifest.json per assignment.
    for folder_name, manifest in manifests.items():
        assignment_folder = Path("attachments") / folder_name
        save_manifest(assignment_folder, manifest)
        print(f"📋 Manifest written: attachments/{folder_name}/manifest.json")

    successful = len(submissions) - len(failed_submissions)
    print(f"\n🎉 Done! {successful}/{len(submissions)} submissions downloaded")
    if failed_submissions:
        print(f"❌ Failed: {len(failed_submissions)} — re-run to retry")

    if args.write_updated_list:
        out_path = ".cache/updated_submissions.json"
        makedirs(".cache", exist_ok=True)
        target_list = updated_submissions if args.only_updated else submissions
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(
                [
                    {
                        "course_id": s["assignment"]["course_id"],
                        "assignment_id": s["assignment"]["id"],
                        "assignment": s["assignment"]["display_name"],
                        "submission_id": s["id"],
                        "student": s["recipient"]["display_name"],
                        "index": s["recipient"]["class"] + s["recipient"]["classnumber"],
                    }
                    for s in target_list
                ],
                f, ensure_ascii=False, indent=2,
            )
        print(f"📝 Updated submission list → {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
