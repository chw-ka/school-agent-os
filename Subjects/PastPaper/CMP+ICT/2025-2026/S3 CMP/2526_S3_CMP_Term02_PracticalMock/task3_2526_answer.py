import json


def build_show(players: list[dict]) -> str:
    sorted_players = sorted(players, key=lambda p: p["score"], reverse=True)
    champion = sorted_players[0]
    runner_up = sorted_players[1]
    team_scores: dict[str, int] = {}
    for p in players:
        team_scores[p["team"]] = team_scores.get(p["team"], 0) + p["score"]
    winner_team = max(team_scores, key=team_scores.get)
    lines = [
        "🎉🎉🎉 遊戲頒獎典禮 🎉🎉🎉",
        "",
        f"🏆 最高分玩家：{champion['name']}（{champion['score']} 分）— {champion['team']}",
        f"🥈 亞軍：{runner_up['name']}（{runner_up['score']} 分）— {runner_up['team']}",
        "",
    ]
    for team, total in team_scores.items():
        lines.append(f"📊 {team}總分：{total}")
    lines.append(f"🎊 恭喜{winner_team}勝出！")
    lines.append("")
    lines.append("（由 Vibe Coding 自動生成）")
    return "\n".join(lines)


def main() -> None:
    with open("game_scores.json", encoding="utf-8") as f:
        players = json.load(f)
    text = build_show(players)
    with open("party_show.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("Wrote party_show.txt")


if __name__ == "__main__":
    main()
