# shared-tools/marking

Auto-marks student homework submissions and pushes results back to the LMS.

## Structure

```
marking/
├── connectors/
│   └── teams/          # MS Teams connector (download, test, submit)
│       └── mygraph/    # MS Graph API client
├── core/
│   └── incremental_state.py   # Resubmission tracking (.cache/)
└── README.md
```

The connector layer is platform-specific (Teams today, Classroom in future).  
The `core/` utilities are platform-agnostic.

## Setup

1. Add MS credentials to the repo-root `.env`:
   ```
   MS_CLIENT_ID=...
   MS_TENANT_ID=...
   MS_SECRET_VALUE=...
   ```

2. Install dependencies (from repo root):
   ```bash
   pip install -r requirements.txt
   ```

## Workflow

All commands run from the **subject's `marking/` directory**, e.g. `Subjects/S3-CMP/marking/`.

### 1. Prepare (first time per year / per session)

```bash
python ../../../shared-tools/marking/connectors/teams/prepare.py
```

Writes two files:
- `platform.json` — Teams course IDs (stable per year, committed)
- `sessions/<name>.session.json` — which assignments to mark (committed)

### 2. Download

```bash
python ../../../shared-tools/marking/connectors/teams/download.py --session 25_26_pai
```

Downloads to `attachments/<assignment>/` using clean filenames: `<class><number>_<original_filename>`.  
Writes `attachments/<assignment>/manifest.json` with full submission metadata.

**Incremental resubmissions:**
```bash
python .../download.py --session 25_26_pai --only-updated --only-submitted --write-updated-list
```

### 3. Test (mark)

```bash
python ../../../shared-tools/marking/connectors/teams/test.py --session 25_26_pai
```

Runs tester modules from the local `tests/` package and writes `marksheets/marksheets_<assignment>.csv`.

### 4. Submit

```bash
python ../../../shared-tools/marking/connectors/teams/submit.py --session 25_26_pai
```

Pushes marks and feedback back to Teams.

## Subject folder layout

```
Subjects/<Form>/marking/
├── platform.json          # committed — Teams course IDs
├── sessions/
│   └── 25_26_term1.session.json   # committed — assignment list
├── tests/
│   ├── __init__.py
│   └── my_tester.py       # committed — marking logic
├── attachments/           # gitignored — downloaded student files
│   └── <assignment>/
│       ├── 3A01_project.aia
│       └── manifest.json
├── aias/                  # gitignored
├── marksheets/            # gitignored
└── .cache/                # gitignored — incremental state
```

## Writing tester modules

Place in `tests/<name>.py`. Export a `test(submissions: pd.DataFrame) -> pd.DataFrame` function:

```python
import pandas as pd

def test(submissions: pd.DataFrame) -> pd.DataFrame:
    for idx, row in submissions.iterrows():
        filepath = row["filepath"]
        # ... mark the file ...
        submissions.at[idx, "marks"] = 8
        submissions.at[idx, "comments"] = "[O] Well done"
    return submissions
```

DataFrame columns: `class`, `classnumber`, `assignment`, `class_id`, `assignment_id`,
`submission_id`, `filepath`, `marks`, `comments`.
