"""
任務三（Vibe Coding）：讀取 game_scores.json，寫入 party_show.txt
請用 Gemini 協助完成；規格見 vibe_spec.md
"""

import json

# TODO: 用 Gemini 完成此程式


def main() -> None:
    with open("game_scores.json", encoding="utf-8") as f:
        players = json.load(f)
    # TODO: 產生有趣文字並寫入 party_show.txt
    raise NotImplementedError("Use Gemini to implement")


if __name__ == "__main__":
    main()
