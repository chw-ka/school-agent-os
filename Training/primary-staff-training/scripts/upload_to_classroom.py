#!/usr/bin/env python3
"""
Upload materials to Google Classroom course.

Usage (run on your local Mac):
    pip install google-api-python-client google-auth-oauthlib
    python scripts/upload_to_classroom.py

First run opens a browser for OAuth consent (Classroom scope).
Token saved to config/classroom-oauth-token.json.
"""

from __future__ import annotations
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEYS_FILE  = ROOT / "config" / "gcp-oauth.keys.json"
TOKEN_FILE = ROOT / "config" / "classroom-oauth-token.json"
HANDOUT_MD = ROOT / "docs" / "participant-handout.md"

# ── Course details ─────────────────────────────────────────────────────────────
COURSE_ID  = "ODU1MjQ4NzE0OTg1"
CLASS_CODE = "zgabqpbr"

SCOPES = [
    "https://www.googleapis.com/auth/classroom.courses",
    "https://www.googleapis.com/auth/classroom.coursework.students",
    "https://www.googleapis.com/auth/classroom.announcements",
    "https://www.googleapis.com/auth/classroom.course-work.readonly",
    "https://www.googleapis.com/auth/drive.file",
]

TASK3_PROMPT = """\
You are coding for M5StickS3 on UIFlow 2 (MicroPython).
Available: BtnA, BtnB, Widgets.Label, Widgets.fillScreen, time, random.
Write a simple reaction game: show "Wait...", after random 1-5 seconds show "GO!" on green screen,
when BtnA pressed after GO show reaction time in milliseconds, if pressed before GO show "Too early!".
Keep it simple for primary students."""

FEEDBACK_URL = "https://docs.google.com/forms/d/e/1FAIpQLSff43JQ-OeTZiGcfMKEM-Pyq_ByyzZ88Tekn4Y1kgGgcDYihw/viewform"

USEFUL_LINKS = """\
UIFlow 2 Web IDE: https://uiflow2.m5stack.com/
小智平台: https://xiaozhi.me/
StickS3 小智教學: https://docs.m5stack.com/zh_CN/guide/realtime/xiaozhi/sticks3
StickS3 UIFlow 2: https://docs.m5stack.com/en/uiflow2/sticks3/program"""


def get_credentials():
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(KEYS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())
    return creds


def build_service(creds):
    from googleapiclient.discovery import build
    return build("classroom", "v1", credentials=creds)


def post_announcement(service, text: str) -> dict:
    body = {
        "courseId": COURSE_ID,
        "text": text,
        "state": "PUBLISHED",
    }
    result = service.courses().announcements().create(
        courseId=COURSE_ID, body=body
    ).execute()
    print(f"  ✅ Announcement posted: {result['id']}")
    return result


def post_material(service, title: str, description: str, link: str | None = None) -> dict:
    material_body = {
        "courseId": COURSE_ID,
        "title": title,
        "description": description,
        "state": "PUBLISHED",
        "topicId": None,
    }
    if link:
        material_body["materials"] = [{"link": {"url": link, "title": title}}]

    result = service.courses().courseWorkMaterials().create(
        courseId=COURSE_ID, body=material_body
    ).execute()
    print(f"  ✅ Material posted: {result['id']} — {title}")
    return result


def main() -> None:
    print("🔐 Authorising Google Classroom API…")
    creds = get_credentials()
    service = build_service(creds)

    print(f"\n📚 Course ID: {COURSE_ID}  (Class Code: {CLASS_CODE})")

    # ── 1. Welcome announcement ────────────────────────────────────────────────
    print("\n1. Posting welcome announcement…")
    welcome = (
        "歡迎參加 STEAM 分享：M5StickS3！\n\n"
        "📅 日期：2026 年 6 月 22 日（一）14:00–15:30\n"
        "📍 地點：元朗朗屏邨惠州學校\n\n"
        "今日三個 Task：\n"
        "  ① Experience — 體驗小智 AI 助手\n"
        "  ② Setup — 安裝 UIFlow 2 + Cloud 配對\n"
        "  ③ Vibe Coding — 用 Gemini 生成反應遊戲\n\n"
        "請記得帶 laptop 連 WiFi！三人一組，現場派 M5StickS3。\n\n"
        f"課後 Feedback：{FEEDBACK_URL}"
    )
    post_announcement(service, welcome)

    # ── 2. Task 3 Sample Prompt ───────────────────────────────────────────────
    print("\n2. Posting Task 3 Sample Prompt material…")
    post_material(
        service,
        title="📋 Task 3 — Gemini Vibe Coding Sample Prompt",
        description=(
            "Copy 以下 prompt 貼入 Gemini 或 UIFlow 2 AI panel：\n\n"
            + TASK3_PROMPT
            + "\n\n"
            "⚠️ 記得先貼 M5StickS3 API context，否則 Gemini 會出錯！"
        ),
    )

    # ── 3. Useful links ────────────────────────────────────────────────────────
    print("\n3. Posting useful links…")
    post_material(
        service,
        title="🔗 有用連結匯總",
        description=USEFUL_LINKS,
        link="https://uiflow2.m5stack.com/",
    )

    # ── 4. Feedback form link ─────────────────────────────────────────────────
    print("\n4. Posting feedback form link…")
    post_material(
        service,
        title="📝 課後 Feedback Form — 請填寫！",
        description="多謝參與！請花 3–5 分鐘填寫 feedback，幫助我們改善未來工作坊。",
        link=FEEDBACK_URL,
    )

    print("\n✅ All done! Check your Google Classroom.")
    print(f"   https://classroom.google.com/c/{COURSE_ID}")


if __name__ == "__main__":
    main()
