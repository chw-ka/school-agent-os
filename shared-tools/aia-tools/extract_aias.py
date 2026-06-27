"""
Extract .aia files from attachments/ into aias/ for all assignments in a session.

Run from a subject's marking directory, e.g. Subjects/S3-CMP/marking/:
    python ../../../shared-tools/aia-tools/extract_aias.py --session 25_26_pai
"""

import json
import sys
import argparse
from pathlib import Path

# Add aia-tools/ to sys.path so aia_util can import blockly_util / components_util.
_AIA_TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(_AIA_TOOLS))

from aia_util import read_aia


def load_session(session_name: str) -> dict:
    session_path = Path("sessions") / f"{session_name}.session.json"
    with session_path.open(encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Extract .aia submissions from attachments/ into aias/")
    parser.add_argument("--session", required=True, help="Session name (e.g. 25_26_pai)")
    args = parser.parse_args()

    session = load_session(args.session)
    Path("aias").mkdir(exist_ok=True)

    for assignment in session["assignments"]:
        assignment_name = assignment["display_name"]
        print(f"Extracting: {assignment_name}")
        try:
            read_aia(assignment_name)
        except Exception as e:
            print(f"  ⚠️  Error: {e}")


if __name__ == "__main__":
    main()
