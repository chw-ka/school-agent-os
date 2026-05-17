"""Local web UI to browse and launch student Python games."""

from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from games_lib import default_games_root, discover_games, launch_game

app = Flask(__name__)

GAMES_ROOT = Path(
    os.environ.get("GAME_LAUNCHER_ROOT", "")
).resolve() if os.environ.get("GAME_LAUNCHER_ROOT") else default_games_root()


@app.route("/")
def index():
    return render_template("index.html", games_root=str(GAMES_ROOT))


@app.route("/api/games")
def api_games():
    games = discover_games(GAMES_ROOT)
    return jsonify({"games": games, "root": str(GAMES_ROOT)})


@app.route("/api/launch", methods=["POST"])
def api_launch():
    data = request.get_json(silent=True) or {}
    relpath = data.get("relpath", "")
    if not relpath or not isinstance(relpath, str):
        return jsonify({"ok": False, "error": "Missing relpath"}), 400
    try:
        launch_game(GAMES_ROOT, relpath)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8765"))
    print(f"Game launcher: http://127.0.0.1:{port}")
    print(f"Games folder: {GAMES_ROOT}")
    app.run(host="127.0.0.1", port=port, debug=False)
