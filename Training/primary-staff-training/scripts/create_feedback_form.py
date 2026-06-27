#!/usr/bin/env python3
"""Create Google Form feedback survey for M5StickS3 STEAM workshop."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config"
TOKEN_PATH = CONFIG / "google-forms-oauth-token.json"
OAUTH_KEYS = CONFIG / "gcp-oauth.keys.json"
OUT_META = ROOT / "docs" / "feedback-form-meta.json"

SCOPES = [
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/drive",
]

FORM_TITLE = "STEAM 分享：M5StickS3 — 工作坊 Feedback"
FORM_DESCRIPTION = (
    "多謝參與 2026 年 6 月 22 日惠州學校 STEAM 分享會。\n"
    "請花 3–5 分鐘填寫，幫助我們改善日後教師培訓。"
)


def load_credentials() -> Credentials:
    if not TOKEN_PATH.exists():
        print(f"Missing OAuth token: {TOKEN_PATH}", file=sys.stderr)
        sys.exit(1)

    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
        print("Refreshed OAuth token.")
    elif creds.expired:
        print("OAuth token expired and no refresh token. Re-authorize required.", file=sys.stderr)
        sys.exit(1)
    return creds


def choice_question(title: str, options: list[str], required: bool = True) -> dict:
    return {
        "title": title,
        "questionItem": {
            "question": {
                "required": required,
                "choiceQuestion": {
                    "type": "RADIO",
                    "options": [{"value": o} for o in options],
                },
            }
        },
    }


def checkbox_question(title: str, options: list[str], required: bool = False) -> dict:
    return {
        "title": title,
        "questionItem": {
            "question": {
                "required": required,
                "choiceQuestion": {
                    "type": "CHECKBOX",
                    "options": [{"value": o} for o in options],
                },
            }
        },
    }


def text_question(title: str, required: bool = False, paragraph: bool = False) -> dict:
    return {
        "title": title,
        "questionItem": {
            "question": {
                "required": required,
                "textQuestion": {"paragraph": paragraph},
            }
        },
    }


def scale_question(title: str, low: int = 1, high: int = 5, required: bool = True) -> dict:
    return {
        "title": title,
        "questionItem": {
            "question": {
                "required": required,
                "scaleQuestion": {
                    "low": low,
                    "high": high,
                    "lowLabel": "非常不同意" if low == 1 else str(low),
                    "highLabel": "非常同意" if high == 5 else str(high),
                },
            }
        },
    }


def build_requests() -> list[dict]:
    return [
        {"createItem": {"item": text_question("學校名稱", required=True), "location": {"index": 0}}},
        {"createItem": {"item": text_question("姓名（可選）", required=False), "location": {"index": 1}}},
        {
            "createItem": {
                "item": scale_question("整體滿意度（1=非常不滿意，5=非常滿意）"),
                "location": {"index": 2},
            }
        },
        {
            "createItem": {
                "item": checkbox_question(
                    "今日完成咗邊啲 Task？",
                    ["Task 1：體驗小智", "Task 2：安裝 UIFlow 2 + Run Once", "Task 3：Gemini Vibe Coding 反應遊戲"],
                ),
                "location": {"index": 3},
            }
        },
        {
            "createItem": {
                "item": scale_question("內容對小學 STEAM / ICT 課堂嘅實用性（1=唔實用，5=好實用）"),
                "location": {"index": 4},
            }
        },
        {
            "createItem": {
                "item": choice_question(
                    "三個 Task 入面，邊個對你最有價值？",
                    ["Task 1：小智體驗", "Task 2：UIFlow 2 配對", "Task 3：Vibe Coding", "三者同等"],
                ),
                "location": {"index": 5},
            }
        },
        {
            "createItem": {
                "item": text_question("今日最有收穫嘅一點係乜？", paragraph=True),
                "location": {"index": 6},
            }
        },
        {
            "createItem": {
                "item": text_question("有邊部分唔清楚或需要更多支援？", paragraph=True),
                "location": {"index": 7},
            }
        },
        {
            "createItem": {
                "item": choice_question(
                    "你有興趣參加進階「Agentic AI / Professional Vibe Coding」課程嗎？",
                    ["有興趣", "可能有興趣", "暫時冇興趣"],
                    required=True,
                ),
                "location": {"index": 8},
            }
        },
        {
            "createItem": {
                "item": text_question("其他意見或建議", paragraph=True),
                "location": {"index": 9},
            }
        },
    ]


def main() -> None:
    creds = load_credentials()
    forms = build("forms", "v1", credentials=creds)

    created = forms.forms().create(body={"info": {"title": FORM_TITLE}}).execute()
    form_id = created["formId"]
    responder_uri = created["responderUri"]
    print(f"Created form: {responder_uri}")

    all_requests = [
        {"updateFormInfo": {"info": {"description": FORM_DESCRIPTION}, "updateMask": "description"}},
        *build_requests(),
    ]
    forms.forms().batchUpdate(formId=form_id, body={"requests": all_requests}).execute()
    print("Added questions.")

    meta = {
        "form_id": form_id,
        "responder_uri": responder_uri,
        "edit_uri": f"https://docs.google.com/forms/d/{form_id}/edit",
        "title": FORM_TITLE,
    }
    OUT_META.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Saved metadata: {OUT_META}")


if __name__ == "__main__":
    main()
