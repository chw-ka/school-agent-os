"""
Submit marks and feedback from marksheets back to Microsoft Teams.

Run from a subject's marking directory, e.g. Subjects/S3-CMP/marking/:
    python ../../../shared-tools/marking/connectors/teams/submit.py --session 25_26_pai
"""

import asyncio
import json
import re
import sys
import argparse
from os import listdir
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

_MARKING_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_MARKING_ROOT))

from connectors.teams.mygraph.client import MSGraphClient
from core.incremental_state import load_state, save_state, mark_submitted, submission_key

client = MSGraphClient(is_application=True)


def load_session(session_name: str) -> dict:
    session_path = Path("sessions") / f"{session_name}.session.json"
    with session_path.open(encoding="utf-8") as f:
        return json.load(f)


def get_total_marks(assignment_display_name: str, session: dict) -> int:
    for a in session.get("assignments", []):
        if a.get("display_name") == assignment_display_name:
            return a.get("total_marks", 10)
    print(f"⚠️ Assignment '{assignment_display_name}' not in session, using default 10")
    return 10


def parse_number_selection(raw, count):
    if raw.lower().strip() == "all":
        return list(range(count))
    indices = []
    seen = set()
    for token in raw.replace(",", " ").split():
        if "-" in token:
            parts = token.split("-")
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                for n in range(int(parts[0]), int(parts[1]) + 1):
                    idx = n - 1
                    if 0 <= idx < count and idx not in seen:
                        indices.append(idx)
                        seen.add(idx)
        elif token.isdigit():
            idx = int(token) - 1
            if 0 <= idx < count and idx not in seen:
                indices.append(idx)
                seen.add(idx)
    return indices


def parse_student_index(index_str):
    m = re.match(r"^(\d)([A-D])(\d{2})$", str(index_str).strip(), re.I)
    if not m:
        return None
    return (int(m.group(1)), m.group(2).upper(), int(m.group(3)))


def make_student_filter(selection_raw):
    raw = selection_raw.strip()
    if not raw or raw.lower() == "all":
        return None
    ranges = []
    for token in re.split(r"[,\s]+", raw):
        if not token:
            continue
        if "-" in token:
            start_s, end_s = token.split("-", 1)
            start = parse_student_index(start_s.strip())
            end = parse_student_index(end_s.strip())
            if not start or not end:
                raise ValueError(f"Invalid student range: {token}")
            if start > end:
                start, end = end, start
            ranges.append((start, end))
        else:
            single = parse_student_index(token)
            if not single:
                raise ValueError(f"Invalid student index: {token}")
            ranges.append((single, single))
    if not ranges:
        raise ValueError(f"Invalid student selection: {selection_raw}")

    def matches(index_str):
        key = parse_student_index(index_str)
        return key is not None and any(s <= key <= e for s, e in ranges)

    return matches


def apply_student_filter(submissions, selection_raw=None):
    if selection_raw is None:
        print("Students to submit (e.g. 3A01-3A10, 3B05, or 'all'):")
        selection_raw = input("Student range: ").strip() or "all"
    try:
        matcher = make_student_filter(selection_raw)
    except ValueError as exc:
        print(f"❌ {exc}")
        return None
    if matcher is None:
        return submissions
    if "index" not in submissions.columns:
        print("⚠️ Marksheet has no 'index' column; cannot filter by student range.")
        return submissions
    filtered = submissions[submissions["index"].apply(matcher)].copy()
    print(f"📋 Filter '{selection_raw}': {len(filtered)} / {len(submissions)} rows")
    if len(filtered) == 0:
        print("❌ No submissions matched.")
        return None
    return filtered


def filter_by_updated_list(submissions: pd.DataFrame, updated_keys: set) -> pd.DataFrame:
    if not updated_keys:
        return submissions
    mask = submissions.apply(
        lambda r: submission_key(str(r["class_id"]), str(r["assignment_id"]), str(r["submission_id"])) in updated_keys,
        axis=1,
    )
    filtered = submissions[mask].copy()
    print(f"🧩 only-updated: {len(filtered)} / {len(submissions)} rows")
    return filtered


def select_marksheets():
    marksheets = sorted(listdir("marksheets"))
    print("Available marksheets:")
    for i, m in enumerate(marksheets):
        print(f"  {i + 1}. {m}")
    print()
    print("Select marksheets (numbers, ranges like 1-3, or 'all'):")
    selection = input("Selection: ").strip()
    if selection.lower() == "all":
        return marksheets
    indices = parse_number_selection(selection, len(marksheets))
    return [marksheets[i] for i in indices]


async def update_assignment_max_score(assignment_id, course_id, assignment_display_name, session):
    total = get_total_marks(assignment_display_name, session)
    try:
        await client.update_assignment_max_score(course_id, assignment_id, total)
        print(f"✅ Max score → {total} for {assignment_display_name}")
        return True
    except Exception as e:
        print(f"❌ Error updating max score: {e}")
        return False


async def submit_single(row):
    try:
        await client.submit_marks(row["class_id"], row["assignment_id"], row["submission_id"], row["marks"])
        await client.submit_comments(row["class_id"], row["assignment_id"], row["submission_id"], row["comments"])
        await client.return_submission(row["class_id"], row["assignment_id"], row["submission_id"])
        return True
    except Exception as e:
        print(f"❌ Error for {row.get('class', '')} {row.get('classnumber', '')}: {e}")
        return False


async def submit(submissions, session):
    unique = submissions[["class_id", "assignment_id", "assignment"]].drop_duplicates()
    print(f"Updating max scores for {len(unique)} assignment(s)...")
    for _, a in unique.iterrows():
        await update_assignment_max_score(a["assignment_id"], a["class_id"], a["assignment"], session)

    batch_size = 10
    rows = [row for _, row in submissions.iterrows()]
    successful = failed = 0
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        results = await asyncio.gather(*[submit_single(r) for r in batch], return_exceptions=True)
        successful += sum(1 for r in results if r is True)
        failed += sum(1 for r in results if r is not True)
        if i + batch_size < len(rows):
            await asyncio.sleep(1)
    print(f"✅ {successful} submitted, {failed} failed")


async def process_marksheets(selected, session, student_range=None, only_updated=False, updated_list_path=".cache/updated_submissions.json"):
    updated_keys = None
    if only_updated:
        p = Path(updated_list_path)
        if p.exists():
            with p.open(encoding="utf-8") as f:
                items = json.load(f)
            updated_keys = {
                submission_key(i["course_id"], i["assignment_id"], i["submission_id"])
                for i in items
                if i.get("course_id") and i.get("assignment_id") and i.get("submission_id")
            }
            print(f"🧩 only-updated: {len(updated_keys)} submissions")
        else:
            print(f"⚠️ Updated list not found at {updated_list_path}. Falling back to full submit.")

    state = load_state()
    for i, marksheet_name in enumerate(selected, 1):
        print(f"\n{'=' * 60}\n{i}/{len(selected)}: {marksheet_name}\n{'=' * 60}")
        try:
            subs = pd.read_csv(f"marksheets/{marksheet_name}")
            if updated_keys is not None:
                subs = filter_by_updated_list(subs, updated_keys)
                if len(subs) == 0:
                    print("ℹ️ No updated rows; skipping.")
                    continue
            subs = apply_student_filter(subs, student_range)
            if subs is None:
                continue
            await submit(subs, session)
            for _, row in subs.iterrows():
                mark_submitted(state, str(row["class_id"]), str(row["assignment_id"]), str(row["submission_id"]),
                               row.get("marks"), row.get("comments"))
            save_state(state)
            if i < len(selected):
                await asyncio.sleep(2)
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    parser = argparse.ArgumentParser(description="Submit marksheets to Teams")
    parser.add_argument("--session", required=True, help="Session name (e.g. 25_26_pai)")
    parser.add_argument("--only-updated", action="store_true")
    parser.add_argument("--updated-list", default=".cache/updated_submissions.json")
    args = parser.parse_args()

    session = load_session(args.session)
    selected = select_marksheets()
    if not selected:
        print("❌ No marksheets selected.")
        return 1

    if len(selected) == 1:
        subs = pd.read_csv(f"marksheets/{selected[0]}")
        if args.only_updated:
            p = Path(args.updated_list)
            if p.exists():
                with p.open(encoding="utf-8") as f:
                    items = json.load(f)
                keys = {
                    submission_key(i["course_id"], i["assignment_id"], i["submission_id"])
                    for i in items
                }
                subs = filter_by_updated_list(subs, keys)
        subs = apply_student_filter(subs)
        if subs is None:
            return 1
        asyncio.run(submit(subs, session))
        state = load_state()
        for _, row in subs.iterrows():
            mark_submitted(state, str(row["class_id"]), str(row["assignment_id"]), str(row["submission_id"]),
                           row.get("marks"), row.get("comments"))
        save_state(state)
    else:
        print(f"Selected {len(selected)} marksheets")
        student_range = input("Student range (e.g. 3A01-3A10 or 'all'): ").strip() or "all"
        asyncio.run(process_marksheets(selected, session, student_range,
                                       only_updated=args.only_updated, updated_list_path=args.updated_list))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
