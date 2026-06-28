"""
Interactive setup: generates platform.json and sessions/<name>.session.json.

Run from a subject's marking directory, e.g. Subjects/S3-CMP/marking/:
    python ../../../shared-tools/marking/connectors/teams/prepare.py

Steps:
  1. Pick or reuse Teams courses
  2. Name the marking session
  3. Pick which assignments to include
  4. Configure tester + marks for each assignment
  5. Write platform.json (courses, stable per year) and sessions/<name>.session.json
"""

import asyncio
import json
import sys
from pathlib import Path

# Make shared-tools/marking/ importable.
_MARKING_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_MARKING_ROOT))

from connectors.teams.mygraph.client import MSGraphClient

client = MSGraphClient(is_application=True)

PLATFORM_FILE = Path("platform.json")
SESSIONS_DIR = Path("sessions")
TESTS_DIR = Path("tests")


# ---------------------------------------------------------------------------
# Tester discovery (from CWD/tests/)
# ---------------------------------------------------------------------------

def discover_testers():
    if not TESTS_DIR.exists():
        return []
    testers = []
    for f in sorted(TESTS_DIR.glob("*.py")):
        if not f.stem.startswith("__"):
            testers.append(f.stem)
    for sub in sorted(TESTS_DIR.iterdir()):
        if sub.is_dir() and not sub.name.startswith("__"):
            for f in sorted(sub.glob("*.py")):
                if not f.stem.startswith("__"):
                    testers.append(f"{sub.name}.{f.stem}")
    return testers


def pick_tester(assignment_name, current_tester, available_testers):
    print(f"\n  Assignment: {assignment_name}")
    print(f"  Current tester: {current_tester or '(none)'}")
    print("\n  Available testers:")
    print("    0. (skip / no test)")
    for i, t in enumerate(available_testers, 1):
        marker = " ◀" if t == current_tester else ""
        print(f"    {i}. {t}{marker}")
    print()
    while True:
        raw = input(f"  Pick tester [0-{len(available_testers)}] (Enter = keep current): ").strip()
        if raw == "":
            return current_tester or ""
        if raw.isdigit():
            idx = int(raw)
            if idx == 0:
                return ""
            if 1 <= idx <= len(available_testers):
                return available_testers[idx - 1]
        print(f"  ⚠️  Enter a number between 0 and {len(available_testers)}")


def pick_total_marks(assignment_name, current_marks):
    default = current_marks if current_marks else 10
    while True:
        raw = input(f"  Total marks for '{assignment_name}' [default {default}]: ").strip()
        if raw == "":
            return default
        if raw.isdigit() and int(raw) > 0:
            return int(raw)
        print("  ⚠️  Enter a positive integer")


# ---------------------------------------------------------------------------
# MS Graph helpers
# ---------------------------------------------------------------------------

async def search_and_pick_courses():
    keywords = input("Search keyword for your Teams (e.g. 'CMP 25-26'): ").strip()
    print("Searching...")
    groups = await client.search_teams(keywords)
    if not groups:
        print("No teams found.")
        return []
    print(f"\nFound {len(groups)} teams:")
    for i, g in enumerate(groups):
        print(f"  {i + 1}. {g.display_name}")
    print()
    raw = input("Pick courses (space-separated numbers, or 'all'): ").strip()
    if raw.lower() == "all":
        return groups
    indices = [int(x) - 1 for x in raw.split() if x.isdigit()]
    return [groups[i] for i in indices if 0 <= i < len(groups)]


async def get_unique_assignments(courses):
    seen = set()
    unique = []
    for course in courses:
        assignments = await client.get_assignments(course.id)
        for a in assignments:
            if a.display_name not in seen:
                seen.add(a.display_name)
                unique.append(a)
    return unique


# ---------------------------------------------------------------------------
# Load / save config
# ---------------------------------------------------------------------------

def load_existing_platform():
    if PLATFORM_FILE.exists():
        with PLATFORM_FILE.open(encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_existing_session(session_name):
    path = SESSIONS_DIR / f"{session_name}.session.json"
    if path.exists():
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    return {}


def pick_assignments(all_assignments, existing_names):
    print("\n" + "=" * 60)
    print(f"Found {len(all_assignments)} assignments — pick which to include")
    print("=" * 60)
    for i, a in enumerate(all_assignments, 1):
        already = " ◀ (in session)" if a.display_name in existing_names else ""
        print(f"  {i:3}. {a.display_name}{already}")
    print()
    print("Enter numbers separated by spaces, ranges like 1-3, or 'all'.")
    raw = input("Select assignments: ").strip()
    if raw.lower() == "all":
        return all_assignments
    selected = []
    seen = set()
    for token in raw.split():
        if "-" in token:
            parts = token.split("-")
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                for n in range(int(parts[0]), int(parts[1]) + 1):
                    if 1 <= n <= len(all_assignments) and n not in seen:
                        selected.append(all_assignments[n - 1])
                        seen.add(n)
        elif token.isdigit():
            n = int(token)
            if 1 <= n <= len(all_assignments) and n not in seen:
                selected.append(all_assignments[n - 1])
                seen.add(n)
    return selected


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main():
    print("=" * 60)
    print("Marking Setup — Teams connector")
    print(f"Working directory: {Path.cwd()}")
    print("=" * 60)

    # --- Platform (courses) ---
    existing_platform = load_existing_platform()
    if existing_platform.get("courses"):
        print("\nExisting courses in platform.json:")
        for c in existing_platform["courses"]:
            print(f"  • {c['display_name']}")
        reuse = input("\nReuse these courses? [Y/n]: ").strip().lower()
        if reuse in ("", "y", "yes"):
            class _Course:
                def __init__(self, d):
                    self.id = d["id"]
                    self.display_name = d["display_name"]
            courses = [_Course(c) for c in existing_platform["courses"]]
        else:
            courses = await search_and_pick_courses()
    else:
        courses = await search_and_pick_courses()

    if not courses:
        print("No courses selected. Exiting.")
        return

    # --- Session name ---
    print()
    existing_sessions = sorted(SESSIONS_DIR.glob("*.session.json")) if SESSIONS_DIR.exists() else []
    if existing_sessions:
        print("Existing sessions:")
        for s in existing_sessions:
            print(f"  • {s.stem.replace('.session', '')}")
    session_name = input("\nSession name (e.g. 25_26_pai or 25_26_s3_pa): ").strip()
    if not session_name:
        print("Session name is required. Exiting.")
        return

    existing_session = load_existing_session(session_name)
    existing_assignments_dict = {
        a["display_name"]: a for a in existing_session.get("assignments", [])
    }

    # --- Assignments ---
    print(f"\nFetching assignments from {len(courses)} course(s)...")
    all_assignments = await get_unique_assignments(courses)
    print(f"Found {len(all_assignments)} unique assignments.\n")
    if not all_assignments:
        print("No assignments found. Exiting.")
        return

    selected_assignments = pick_assignments(all_assignments, set(existing_assignments_dict))
    if not selected_assignments:
        print("No assignments selected.")
        return

    # --- Testers + marks ---
    available_testers = discover_testers()
    new_assignments = []
    print("\n" + "=" * 60)
    print("Configure tester for each selected assignment")
    print("=" * 60)
    for a in selected_assignments:
        existing_a = existing_assignments_dict.get(a.display_name, {})
        tester = pick_tester(a.display_name, existing_a.get("tester", ""), available_testers)
        marks = pick_total_marks(a.display_name, existing_a.get("total_marks", 10))
        new_assignments.append({
            "display_name": a.display_name,
            "tester": tester,
            "total_marks": marks,
        })

    report_settings = existing_session.get("report_settings", {"show_code_column": False})

    # --- Preview + save ---
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    for a in new_assignments:
        label = a["tester"] if a["tester"] else "(no test)"
        print(f"  {a['display_name']}")
        print(f"    tester: {label}   total_marks: {a['total_marks']}")

    confirm = input("\nSave? [Y/n]: ").strip().lower()
    if confirm not in ("", "y", "yes"):
        print("Cancelled.")
        return

    platform_data = {
        "platform": "teams",
        "courses": [{"id": c.id, "display_name": c.display_name} for c in courses],
    }
    with PLATFORM_FILE.open("w", encoding="utf-8") as f:
        json.dump(platform_data, f, ensure_ascii=False, indent=4)
    print(f"✅ Saved platform.json")

    SESSIONS_DIR.mkdir(exist_ok=True)
    session_path = SESSIONS_DIR / f"{session_name}.session.json"
    session_data = {
        "assignments": new_assignments,
        "report_settings": report_settings,
    }
    with session_path.open("w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=4)
    print(f"✅ Saved sessions/{session_name}.session.json")


if __name__ == "__main__":
    asyncio.run(main())
