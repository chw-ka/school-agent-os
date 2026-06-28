"""Create a Google Form from a JSON spec using OAuth credentials in configs/."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OAUTH_KEYS = REPO_ROOT / "configs" / "gcp-oauth.keys.json"
DEFAULT_TOKEN = REPO_ROOT / "configs" / "google-forms-oauth-token.json"
SCOPES = [
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/drive",
]


def _load_spec(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Spec must be a JSON object.")
    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError('Spec must contain non-empty string field "title".')
    questions = data.get("questions")
    if not isinstance(questions, list) or not questions:
        raise ValueError('Spec must contain non-empty array field "questions".')
    return data


def _load_credentials(oauth_keys: Path, token_path: Path) -> Credentials:
    if not oauth_keys.is_file():
        raise FileNotFoundError(f"OAuth client secrets not found: {oauth_keys}")
    if not token_path.is_file():
        raise FileNotFoundError(
            f"OAuth token not found: {token_path}\n"
            "Run the one-time browser auth flow first (see README)."
        )

    keys = json.loads(oauth_keys.read_text(encoding="utf-8"))
    installed = keys.get("installed") or keys
    token_data = json.loads(token_path.read_text(encoding="utf-8"))

    creds = Credentials(
        token=token_data.get("token"),
        refresh_token=token_data.get("refresh_token"),
        token_uri=token_data.get("token_uri") or installed.get("token_uri"),
        client_id=token_data.get("client_id") or installed.get("client_id"),
        client_secret=token_data.get("client_secret") or installed.get("client_secret"),
        scopes=token_data.get("scopes") or SCOPES,
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_data.update(
            {
                "token": creds.token,
                "refresh_token": creds.refresh_token,
                "expiry": creds.expiry.isoformat() if creds.expiry else None,
            }
        )
        token_path.write_text(json.dumps(token_data, ensure_ascii=False), encoding="utf-8")
    return creds


def _item_from_question(q: dict[str, Any]) -> dict[str, Any]:
    qtype = q.get("type")
    title = q.get("title", "")
    description = q.get("description", "")

    if qtype == "section":
        return {
            "title": title,
            "description": description,
            "pageBreakItem": {},
        }

    if qtype == "description":
        return {
            "title": title,
            "description": description,
            "textItem": {},
        }

    required = bool(q.get("required", False))
    question: dict[str, Any] = {"required": required}

    if qtype in ("text", "paragraph"):
        question["textQuestion"] = {"paragraph": qtype == "paragraph"}
    elif qtype == "choice":
        choice_type = (q.get("choice_type") or "RADIO").upper()
        if choice_type not in {"RADIO", "CHECKBOX", "DROP_DOWN"}:
            raise ValueError(f'Invalid choice_type "{choice_type}" for question "{title}".')
        options = q.get("options")
        if not isinstance(options, list) or not options:
            raise ValueError(f'Choice question "{title}" must have non-empty "options".')
        question["choiceQuestion"] = {
            "type": choice_type,
            "options": [{"value": str(opt)} for opt in options],
            "shuffle": bool(q.get("shuffle", False)),
        }
    else:
        raise ValueError(f'Unknown question type "{qtype}" for "{title}".')

    item: dict[str, Any] = {
        "title": title,
        "questionItem": {"question": question},
    }
    if description:
        item["description"] = description
    return item


def _build_create_requests(questions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    requests: list[dict[str, Any]] = []
    for idx, q in enumerate(questions):
        requests.append(
            {
                "createItem": {
                    "item": _item_from_question(q),
                    "location": {"index": idx},
                }
            }
        )
    return requests


def create_form_from_spec(
    spec: dict[str, Any],
    *,
    oauth_keys: Path = DEFAULT_OAUTH_KEYS,
    token_path: Path = DEFAULT_TOKEN,
) -> dict[str, str]:
    creds = _load_credentials(oauth_keys, token_path)
    service = build("forms", "v1", credentials=creds, cache_discovery=False)

    create_body: dict[str, Any] = {
        "info": {
            "title": spec["title"].strip(),
        }
    }
    document_title = spec.get("document_title")
    if isinstance(document_title, str) and document_title.strip():
        create_body["info"]["documentTitle"] = document_title.strip()

    created = service.forms().create(body=create_body).execute()
    form_id = created["formId"]

    requests: list[dict[str, Any]] = []
    info_update: dict[str, Any] = {}
    description = spec.get("description")
    if isinstance(description, str) and description.strip():
        info_update["description"] = description.strip()
    if info_update:
        requests.append(
            {
                "updateFormInfo": {
                    "info": info_update,
                    "updateMask": ",".join(info_update.keys()),
                }
            }
        )
    requests.extend(_build_create_requests(spec["questions"]))
    if requests:
        service.forms().batchUpdate(formId=form_id, body={"requests": requests}).execute()

    responder_url = created.get("responderUri") or f"https://docs.google.com/forms/d/{form_id}/viewform"
    edit_url = created.get("editUri") or f"https://docs.google.com/forms/d/{form_id}/edit"
    return {
        "form_id": form_id,
        "title": spec["title"],
        "responder_url": responder_url,
        "edit_url": edit_url,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a Google Form from a JSON spec.")
    parser.add_argument("spec", type=Path, help="Path to form spec JSON")
    parser.add_argument("--oauth-keys", type=Path, default=DEFAULT_OAUTH_KEYS)
    parser.add_argument("--token", type=Path, default=DEFAULT_TOKEN)
    parser.add_argument("--json-out", type=Path, help="Write result metadata to this JSON file")
    args = parser.parse_args(argv)

    spec = _load_spec(args.spec)
    result = create_form_from_spec(spec, oauth_keys=args.oauth_keys, token_path=args.token)

    print(f"Created: {result['title']}")
    print(f"Form ID: {result['form_id']}")
    print(f"填寫連結: {result['responder_url']}")
    print(f"編輯連結: {result['edit_url']}")

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Metadata: {args.json_out}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
