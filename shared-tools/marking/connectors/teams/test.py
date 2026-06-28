"""
Run marking tests and generate marksheets.

Run from a subject's marking directory, e.g. Subjects/S3-CMP/marking/:
    python ../../../shared-tools/marking/connectors/teams/test.py --session 25_26_pai

File paths are resolved from the assignment's manifest.json (no Graph API call for filepaths).
Testers are imported from the local tests/ package in the working directory.
"""

import asyncio
import importlib
import json
import re
import sys
import time
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

_MARKING_ROOT = Path(__file__).resolve().parents[2]
_SHARED_TOOLS = _MARKING_ROOT.parent
sys.path.insert(0, str(_MARKING_ROOT))
# Expose shared utility packages to tester modules.
sys.path.insert(0, str(_SHARED_TOOLS / "aia-tools"))
sys.path.insert(0, str(_SHARED_TOOLS / "code-marking"))
# Add CWD so local tests/ package is importable.
sys.path.insert(0, str(Path.cwd()))

from connectors.teams.mygraph.client import MSGraphClient
from core.incremental_state import load_state, get_submission_state, submission_key

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

client = MSGraphClient(is_application=True)

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


def import_tests(modules):
    return [importlib.import_module("." + x, package="tests") for x in modules]


def load_manifest_filepaths(assignment_name: str) -> dict:
    """Return {submission_id: stored_path} from the assignment's manifest.json."""
    folder = Path("attachments") / safe_foldername(assignment_name)
    manifest_path = folder / "manifest.json"
    if not manifest_path.exists():
        return {}
    with manifest_path.open(encoding="utf-8") as f:
        data = json.load(f)
    result = {}
    for sub in data.get("submissions", []):
        files = sub.get("files", [])
        if files:
            stored = str(folder / files[-1]["stored_filename"])
            result[sub["submission_id"]] = stored
    return result


def rubric_column_name(section):
    return f"{section['name']} ({section['max_marks']})"


def apply_rubric_columns(marksheets, tester):
    rubric = getattr(tester, "RUBRIC", None)
    if not rubric:
        return marksheets, None
    rename_map = {}
    sections = []
    for section in rubric:
        key = section["key"]
        col_name = rubric_column_name(section)
        if key in marksheets.columns:
            rename_map[key] = col_name
        sections.append({"key": key, "column": col_name, "name": section["name"], "max_marks": section["max_marks"]})
    if rename_map:
        marksheets = marksheets.rename(columns=rename_map)
    return marksheets, sections


def save_rubric_metadata(assignment_name, sections):
    if not sections:
        return
    rubric_path = f"marksheets/marksheets_{assignment_name}_rubric.json"
    with open(rubric_path, "w", encoding="utf-8") as f:
        json.dump({"sections": sections}, f, ensure_ascii=False, indent=2)


async def get_all_members(course_id):
    members = await client.get_group_members(course_id)
    return [
        {
            "id": m.id,
            "display_name": m.display_name,
            "class": m.display_name[0:2],
            "classnumber": m.display_name[2:4],
        }
        for m in members
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
        }
        for s in submissions
    ]


async def main():
    parser = argparse.ArgumentParser(description="Run auto-marking tests and generate marksheets")
    parser.add_argument("--session", required=True, help="Session name (e.g. 25_26_pai)")
    parser.add_argument("--only-updated", action="store_true")
    parser.add_argument("--updated-list", default=".cache/updated_submissions.json")
    parser.add_argument("--use-state-filepaths", action="store_true",
                        help="Fall back to incremental state for filepaths when manifest entry is missing")
    parser.add_argument("--output-incremental", action="store_true")
    parser.add_argument("--incremental-dir", default="marksheets/incremental")
    args = parser.parse_args()

    platform, session = load_config(args.session)
    courses = platform["courses"]
    state = load_state()

    updated_keys = None
    if args.only_updated:
        p = Path(args.updated_list)
        if p.exists():
            with p.open(encoding="utf-8") as f:
                updated_items = json.load(f)
            updated_keys = {
                submission_key(i["course_id"], i["assignment_id"], i["submission_id"])
                for i in updated_items
                if i.get("course_id") and i.get("assignment_id") and i.get("submission_id")
            }
            print(f"🧩 only-updated: {len(updated_keys)} submissions")
        else:
            print(f"⚠️ Updated list not found at {p}. Falling back to full re-test.")

    members = []
    for course in courses:
        members += await get_all_members(course["id"])
    print(f"{len(members)} members loaded")
    members_dict = {m["id"]: m for m in members}

    available_assignments = [a["display_name"] for a in session["assignments"]]
    tester_names = [a["tester"] if a["tester"] else "no_test" for a in session["assignments"]]
    available_testers = import_tests(tester_names)

    assignments = []
    for course in courses:
        ms_assignments = await get_all_assignments(course["id"])
        assignments += [
            {
                "id": a["id"],
                "course_id": course["id"],
                "display_name": a["display_name"],
                "tester": available_testers[available_assignments.index(a["display_name"])],
            }
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

    # Pre-load manifest filepaths for all assignments.
    manifest_paths: dict[str, dict] = {
        name: load_manifest_filepaths(name) for name in available_assignments
    }

    columns = ["index", "class", "classnumber"] + available_assignments
    form = courses[0]["display_name"][0]
    classes = ["A", "B", "C", "D"]
    df = pd.DataFrame(columns=columns)
    for c in classes:
        for cn in range(1, 35):
            row = [str(form) + c + f"{cn:02}", str(form) + c, cn] + [0] * len(available_assignments)
            df.loc[-1] = row
            df.index = df.index + 1
            df = df.sort_index()
    df = df.set_index("index")

    content = []
    for submission in submissions:
        assignment_name = submission["assignment"]["display_name"]
        sub_id = submission["id"]

        # Resolve filepath: manifest first, incremental state as fallback.
        fp = manifest_paths.get(assignment_name, {}).get(sub_id)
        if fp is None and args.use_state_filepaths:
            st = get_submission_state(
                state,
                submission["assignment"]["course_id"],
                submission["assignment"]["id"],
                sub_id,
            )
            fp = st.latest_filepath

        recipient = submission["recipient"]
        content.append([
            recipient["class"] + recipient["classnumber"],
            recipient["class"],
            recipient["classnumber"],
            assignment_name,
            submission["assignment"]["course_id"],
            submission["assignment"]["id"],
            sub_id,
            fp,
            0,
            "",
        ])

    submissions_df = pd.DataFrame(
        content,
        columns=["index", "class", "classnumber", "assignment", "class_id",
                 "assignment_id", "submission_id", "filepath", "marks", "comments"],
    )
    print(submissions_df[["class", "classnumber", "assignment", "filepath"]])

    def process_assignment(assignment_data):
        assignment_name, tester = assignment_data
        print(f"Starting: {assignment_name}")
        asgn_subs = submissions_df[submissions_df["assignment"] == assignment_name]
        if len(asgn_subs) == 0:
            return assignment_name, pd.DataFrame(), None

        if updated_keys is not None:
            keep = asgn_subs.apply(
                lambda r: submission_key(r["class_id"], r["assignment_id"], r["submission_id"]) in updated_keys,
                axis=1,
            )
            asgn_subs = asgn_subs[keep]
            print(f"only-updated: {assignment_name} → {len(asgn_subs)} submissions")
            if len(asgn_subs) == 0:
                return assignment_name, pd.DataFrame(), None

        marksheets = tester.test(asgn_subs).set_index("index")
        marksheets, rubric_sections = apply_rubric_columns(marksheets, tester)

        base_cols = ["class", "classnumber", "assignment", "class_id",
                     "assignment_id", "submission_id", "filepath", "comments", "marks"]
        results = marksheets[base_cols].copy()
        for col in marksheets.columns:
            if col not in results.columns and (col.startswith("mark") or (" (" in col and col.endswith(")"))):
                results[col] = marksheets[col]

        print(f"Done: {assignment_name} ({len(results)} submissions)")
        return assignment_name, results, rubric_sections

    assignment_data = [
        (name, available_testers[available_assignments.index(name)])
        for name in available_assignments
    ]
    n = len(available_assignments)
    max_workers = 2 if n >= 6 else (3 if n >= 4 else min(n, 4))
    print(f"Processing {n} assignments with {max_workers} workers...")

    start = time.time()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_assignment, assignment_data))
    print(f"✅ All done in {time.time() - start:.2f}s")

    assignment_total_marks = {a["display_name"]: a.get("total_marks", 10) for a in session["assignments"]}

    Path("marksheets").mkdir(exist_ok=True)

    def save_and_update(result):
        assignment_name, results_marksheets, rubric_sections = result
        if updated_keys is not None and args.output_incremental:
            Path(args.incremental_dir).mkdir(parents=True, exist_ok=True)
            out_path = str(Path(args.incremental_dir) / f"marksheets_{safe_foldername(assignment_name)}.csv")
        else:
            out_path = f"marksheets/marksheets_{assignment_name}.csv"

        if updated_keys is not None and len(results_marksheets) == 0:
            return assignment_name, results_marksheets

        if updated_keys is not None and args.output_incremental:
            results_marksheets.to_csv(out_path, index=False)
            save_rubric_metadata(assignment_name, rubric_sections)
            return assignment_name, results_marksheets

        if updated_keys is not None and Path(out_path).exists():
            existing = pd.read_csv(out_path)
            if "index" in existing.columns:
                existing = existing.set_index("index")
            else:
                results_marksheets.to_csv(out_path)
                save_rubric_metadata(assignment_name, rubric_sections)
                return assignment_name, results_marksheets
            if len(results_marksheets) > 0:
                missing = results_marksheets.index.difference(existing.index)
                for idx in missing:
                    existing.loc[idx, :] = None
                for col in results_marksheets.columns:
                    existing.loc[results_marksheets.index, col] = results_marksheets[col]
            existing.reset_index().to_csv(out_path, index=False)
        else:
            results_marksheets.to_csv(out_path)

        save_rubric_metadata(assignment_name, rubric_sections)
        return assignment_name, results_marksheets

    with ThreadPoolExecutor(max_workers=8) as executor:
        saved = list(executor.map(save_and_update, results))

    for assignment_name, results_marksheets in saved:
        if len(results_marksheets) > 0:
            valid = results_marksheets.index.intersection(df.index)
            if len(valid) > 0:
                df.loc[valid, assignment_name] = results_marksheets.loc[valid, "marks"]

    df = df.sort_index()

    print("\nSummary:")
    for name in available_assignments:
        avg = df[name].mean()
        count = df[name].count()
        total = assignment_total_marks.get(name, 10)
        print(f"  {name}: avg {avg:.2f}/{total} ({count} submissions)")

    df.to_csv("results.csv")
    print("Results saved to results.csv")


if __name__ == "__main__":
    asyncio.run(main())
