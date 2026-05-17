"""Simple desktop launcher (tkinter) — no browser required."""

from __future__ import annotations

import os
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from games_lib import default_games_root, discover_games, launch_game

GAMES_ROOT = Path(
    os.environ.get("GAME_LAUNCHER_ROOT", "")
).resolve() if os.environ.get("GAME_LAUNCHER_ROOT") else default_games_root()


def main() -> None:
    games = discover_games(GAMES_ROOT)
    root = tk.Tk()
    root.title("第五章 任務三 — 遊戲展示")
    root.geometry("720x520")
    root.minsize(480, 360)

    frm = ttk.Frame(root, padding=12)
    frm.pack(fill=tk.BOTH, expand=True)

    ttk.Label(
        frm,
        text=f"資料夾：{GAMES_ROOT}",
        wraplength=680,
        font=("Segoe UI", 9),
    ).pack(anchor=tk.W)

    ttk.Label(frm, text="雙擊或按「開啟遊戲」執行選取的 .py 檔案。").pack(
        anchor=tk.W, pady=(8, 4)
    )

    columns = ("title", "file")
    tree = ttk.Treeview(frm, columns=columns, show="headings", height=18, selectmode=tk.BROWSE)
    tree.heading("title", text="作品 / 姓名")
    tree.heading("file", text="檔名")
    tree.column("title", width=360)
    tree.column("file", width=300)

    scroll = ttk.Scrollbar(frm, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)

    row_frame = ttk.Frame(frm)
    row_frame.pack(fill=tk.BOTH, expand=True, pady=8)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    relpath_by_iid: dict[str, str] = {}
    for g in games:
        iid = tree.insert("", tk.END, values=(g["title"], g["filename"]))
        relpath_by_iid[iid] = g["relpath"]

    def do_launch() -> None:
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("提示", "請先選取一個遊戲。")
            return
        rel = relpath_by_iid.get(sel[0])
        if not rel:
            return
        try:
            launch_game(GAMES_ROOT, rel)
        except ValueError as e:
            messagebox.showerror("無法啟動", str(e))

    tree.bind("<Double-1>", lambda e: do_launch())

    btn_row = ttk.Frame(frm)
    btn_row.pack(fill=tk.X)
    ttk.Button(btn_row, text="開啟遊戲", command=do_launch).pack(side=tk.LEFT)
    ttk.Button(btn_row, text="結束", command=root.quit).pack(side=tk.RIGHT)

    if not games:
        messagebox.showwarning(
            "沒有遊戲",
            f"在下列資料夾找不到 .py：\n{GAMES_ROOT}",
        )

    root.mainloop()


if __name__ == "__main__":
    main()
    sys.exit(0)
