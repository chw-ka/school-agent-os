
import tkinter as tk
from tkinter import messagebox, ttk
import random
import time

# ===================== 武将库 =====================
HEROES = {
    "刘备": {
        "max_hp": 4,
        "skill": "仁德：出牌阶段可将任意手牌交给对方",
        "color": "#8B4513"
    },
    "关羽": {
        "max_hp": 4,
        "skill": "武圣：红色牌可当【杀】使用",
        "color": "#DC143C"
    },
    "张飞": {
        "max_hp": 4,
        "skill": "咆哮：出牌阶段可使用任意张【杀】",
        "color": "#8B0000"
    },
    "曹操": {
        "max_hp": 4,
        "skill": "奸雄：受到伤害后可获得造成伤害的牌",
        "color": "#4682B4"
    },
    "司马懿": {
        "max_hp": 3,
        "skill": "反馈：受到伤害后摸1张牌",
        "color": "#4B0082"
    },
    "郭嘉": {
        "max_hp": 3,
        "skill": "遗计：受到伤害后摸2张牌",
        "color": "#87CEEB"
    }
}

CARDS = ["杀", "杀", "杀", "闪", "闪", "桃", "桃", "酒"]

# ===================== 主游戏 =====================
class SanGuoShaGame:
    def __init__(self, root):
        self.root = root
        self.root.title("三国杀 - 司马懿+郭嘉卖血版")
        self.root.geometry("1000x720")
        self.root.resizable(False, False)
        self.hero_select_window()

    # ===================== 角色选择 =====================
    def hero_select_window(self):
        self.select_win = tk.Toplevel(self.root)
        self.select_win.title("选择你的武将")
        self.select_win.geometry("500x400")
        self.select_win.resizable(False, False)

        tk.Label(self.select_win, text="请选择你的武将", font=("微软雅黑",16,"bold")).pack(pady=10)
        self.hero_var = tk.StringVar()
        frame = tk.Frame(self.select_win)
        frame.pack(pady=10)

        row, col = 0, 0
        for hero in HEROES:
            btn = tk.Radiobutton(frame, text=f"{hero}\n{HEROES[hero]['skill']}",
                                 variable=self.hero_var, value=hero, width=22, height=3,
                                 font=("微软雅黑",9), bg=HEROES[hero]["color"], fg="white")
            btn.grid(row=row, column=col, padx=5, pady=5)
            col += 1
            if col >= 2:
                col = 0
                row += 1

        tk.Button(self.select_win, text="确定选择", command=self.confirm_hero,
                  font=("微软雅黑",12,"bold"), bg="gold", width=12).pack(pady=15)

    def confirm_hero(self):
        selected = self.hero_var.get()
        if not selected:
            messagebox.showwarning("提示","请先选择一个武将！")
            return
        self.player_hero = selected
        self.select_win.destroy()
        self.com_hero = random.choice([h for h in HEROES if h != selected])
        self.init_game()

    # ===================== 游戏初始化 =====================
    def init_game(self):
        self.players = ["玩家", "电脑"]
        self.current_player = 0
        self.hp = {
            "玩家": HEROES[self.player_hero]["max_hp"],
            "电脑": HEROES[self.com_hero]["max_hp"]
        }
        self.hero = {"玩家": self.player_hero, "电脑": self.com_hero}
        self.drunk = {"玩家": False, "电脑": False}
        self.pending_damage = 0
        self.pending_attacker = None

        # 开局4张手牌
        self.hands = {
            "玩家": random.sample(CARDS, 4),
            "电脑": random.sample(CARDS, 4)
        }

        # 每回合只能出一次杀
        self.used_slash = {"玩家": False, "电脑": False}

        self.create_widgets()
        self.start_game()

    def create_widgets(self):
        title_label = tk.Label(self.root, text="三 国 杀", font=("微软雅黑",26,"bold"), fg="red")
        title_label.pack(pady=5)

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.info_frame = tk.Frame(main_frame, bd=2, relief=tk.GROOVE)
        self.info_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        game_frame = tk.Frame(main_frame)
        game_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.enemy_frame = tk.Frame(game_frame, bd=2, relief=tk.GROOVE)
        self.enemy_frame.pack(fill=tk.X, pady=5)

        log_label = tk.Label(game_frame, text="游戏日志", font=("微软雅黑",10,"bold"))
        log_label.pack()
        self.log_text = tk.Text(game_frame, height=11, width=88, font=("微软雅黑",9))
        self.log_text.pack(fill=tk.X, pady=2)
        self.log_text.config(state=tk.DISABLED)

        self.hand_frame = tk.Frame(game_frame, bd=2, relief=tk.GROOVE)
        self.hand_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        btn_frame = tk.Frame(game_frame)
        btn_frame.pack(fill=tk.X, pady=3)
        self.draw_btn = tk.Button(btn_frame, text="摸2张牌", command=self.draw_cards, width=10)
        self.draw_btn.pack(side=tk.LEFT, padx=5)
        self.skill_btn = tk.Button(btn_frame, text="使用技能", command=self.use_skill, width=10, bg="gold")
        self.skill_btn.pack(side=tk.LEFT, padx=5)
        self.end_btn = tk.Button(btn_frame, text="结束回合", command=self.end_turn, width=10, bg="lightblue")
        self.end_btn.pack(side=tk.LEFT, padx=5)

        self.defend_frame = tk.Frame(game_frame)
        self.dodge_btn = tk.Button(self.defend_frame, text="使用【闪】抵挡", command=self.use_dodge,
                                   bg="lightgreen", width=18, font=("微软雅黑",9))

        self.refresh_hero_info()

    def refresh_hero_info(self):
        for w in self.info_frame.winfo_children(): w.destroy()
        for w in self.enemy_frame.winfo_children(): w.destroy()
        for w in self.hand_frame.winfo_children(): w.destroy()

        me, enemy = "玩家", "电脑"

        tk.Label(self.info_frame, text="你的武将", font=("微软雅黑",11,"bold")).pack(pady=3)
        tk.Label(self.info_frame, text=self.hero[me], font=("微软雅黑",14,"bold"),
                 bg=HEROES[self.hero[me]]["color"], fg="white", width=8).pack(pady=2)
        tk.Label(self.info_frame, text=f"血量：{self.hp[me]}/{HEROES[self.hero[me]]['max_hp']}",
                 fg="red", font=("微软雅黑",10)).pack(pady=2)
        if self.drunk["玩家"]:
            tk.Label(self.info_frame, text="已喝酒\n下张杀伤害+1", fg="purple", font=("微软雅黑",9)).pack(pady=2)

        tk.Label(self.enemy_frame, text="电脑武将：", font=("微软雅黑",11)).grid(row=0, column=0, padx=5)
        tk.Label(self.enemy_frame, text=self.hero[enemy], font=("微软雅黑",12,"bold"),
                 bg=HEROES[self.hero[enemy]]["color"], fg="white").grid(row=0, column=1, padx=5)
        tk.Label(self.enemy_frame, text=f"血量：{self.hp[enemy]}/{HEROES[self.hero[enemy]]['max_hp']}",
                 fg="red", font=("微软雅黑",10)).grid(row=0, column=2, padx=10)
        tk.Label(self.enemy_frame, text=f"手牌：{len(self.hands[enemy])}张",
                 font=("微软雅黑",10)).grid(row=0, column=3, padx=5)
        if self.drunk["电脑"]:
            tk.Label(self.enemy_frame, text="已喝酒", fg="purple", font=("微软雅黑",9)).grid(row=0, column=4, padx=5)

        tk.Label(self.hand_frame, text="你的手牌", font=("微软雅黑",10,"bold")).pack(anchor=tk.W)
        for card in self.hands["玩家"]:
            btn = tk.Button(self.hand_frame, text=card, width=6, height=2,
                            command=lambda c=card: self.use_card(c))
            btn.pack(side=tk.LEFT, padx=3, pady=3)

    def add_log(self, text):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"• {text}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def start_game(self):
        self.add_log(f"游戏开始！你：【{self.player_hero}】，电脑：【{self.com_hero}】")
        self.add_log("开局每人4张手牌")
        self.add_log("========== 你的回合 ==========")
        self.refresh_hero_info()

    def draw_cards(self):
        p = self.players[self.current_player]
        if len(self.hands[p]) >= 10:
            self.add_log("手牌已满")
            return
        new = random.sample(CARDS, 2)
        self.hands[p].extend(new)
        self.add_log(f"{p}摸牌：{new}")
        self.refresh_hero_info()
        self.draw_btn.config(state=tk.DISABLED)

    # ===================== 使用卡牌 =====================
    def use_card(self, card):
        me, enemy = "玩家", "电脑"
        if card not in self.hands[me]:
            return

        if card == "酒":
            if self.drunk[me]:
                self.add_log("本回合已喝过酒！")
                return
            self.hands[me].remove("酒")
            self.drunk[me] = True
            self.add_log("你使用【酒】，下张【杀】伤害+1！")
            self.refresh_hero_info()
            return

        if card == "杀":
            if self.hero[me] != "张飞" and self.used_slash[me]:
                self.add_log("本回合已经使用过【杀】，无法再出！")
                return

            self.hands[me].remove(card)
            self.used_slash[me] = True
            dmg = 2 if self.drunk[me] else 1
            self.drunk[me] = False
            self.add_log(f"你对电脑使用【杀】，即将造成{dmg}点伤害！")
            self.root.update()
            time.sleep(0.5)
            self.enemy_dodge_check("玩家", "电脑", dmg)
            self.refresh_hero_info()
            return

        if card == "桃":
            if self.hp[me] >= HEROES[self.hero[me]]["max_hp"]:
                self.add_log("血量已满，无法使用桃")
                return
            self.hands[me].remove("桃")
            self.hp[me] += 1
            self.add_log("你使用【桃】，恢复1点血量")
            self.refresh_hero_info()
            return

        if card == "闪":
            self.add_log("当前没有杀指向你，无法使用闪")
            return

    # ===================== 卖血技能核心 =====================
    def trigger_hero_skill(self, who, dmg):
        """ 受到伤害后触发司马懿/郭嘉技能 """
        hero = self.hero[who]
        if hero == "司马懿":
            # 反馈：受 dmg 点伤害 → 摸 1 张
            add = random.choice(CARDS)
            self.hands[who].append(add)
            self.add_log(f"【司马懿·反馈】受到{dmg}点伤害，摸1张牌：{add}")
        elif hero == "郭嘉":
            # 遗计：受 dmg 点伤害 → 摸 2 张
            add1 = random.choice(CARDS)
            add2 = random.choice(CARDS)
            self.hands[who].extend([add1, add2])
            self.add_log(f"【郭嘉·遗计】受到{dmg}点伤害，摸2张牌：{add1}, {add2}")
        elif hero == "曹操":
            # 奸雄：获得造成伤害的牌（这里简化为摸1张）
            add = random.choice(CARDS)
            self.hands[who].append(add)
            self.add_log(f"【曹操·奸雄】受到伤害，摸1张牌：{add}")
        self.refresh_hero_info()

    # ===================== 闪避机制 =====================
    def enemy_dodge_check(self, attacker, defender, damage):
        self.pending_attacker = attacker
        self.pending_damage = damage

        if defender == "电脑":
            if "闪" in self.hands["电脑"]:
                self.hands["电脑"].remove("闪")
                self.add_log("电脑使用【闪】，挡住了你的杀！")
                self.pending_damage = 0
            else:
                self.add_log("电脑没有闪，受到伤害！")
                self.hp["电脑"] -= damage
                # 电脑卖血技能
                if damage > 0:
                    self.trigger_hero_skill("电脑", damage)
                self.check_death()
        else:
            self.add_log("电脑对你使用杀！你可以出【闪】抵挡")
            self.disable_player_buttons()
            self.defend_frame.pack(pady=5)
            self.dodge_btn.pack()
            self.root.update()

    def use_dodge(self):
        if "闪" not in self.hands["玩家"]:
            self.add_log("你没有闪了！")
            self.take_damage()
            return
        self.hands["玩家"].remove("闪")
        self.add_log("你使用【闪】，成功抵挡杀！")
        self.pending_damage = 0
        self.defend_frame.forget()
        self.dodge_btn.pack_forget()
        self.root.after(500, self.continue_after_defend)

    def take_damage(self):
        self.defend_frame.forget()
        self.dodge_btn.pack_forget()
        dmg = self.pending_damage
        self.hp["玩家"] -= dmg
        self.add_log(f"你受到{dmg}点伤害！")
        # 玩家卖血技能
        if dmg > 0:
            self.trigger_hero_skill("玩家", dmg)
        self.check_death()
        self.root.after(500, self.continue_after_defend)

    def continue_after_defend(self):
        self.pending_damage = 0
        self.pending_attacker = None
        self.enable_player_buttons()
        self.refresh_hero_info()

    # ===================== 技能 =====================
    def use_skill(self):
        me, enemy = "玩家", "电脑"
        hero = self.hero["玩家"]

        if hero == "刘备":
            if not self.hands[me]:
                self.add_log("没有手牌无法发动仁德")
                return
            card = self.hands[me].pop(0)
            self.hands[enemy].append(card)
            self.add_log(f"刘备发动【仁德】，交给电脑【{card}】")

        elif hero == "张飞":
            self.add_log("张飞【咆哮】：本回合可无限出杀！")

        elif hero == "关羽":
            self.add_log("关羽【武圣】：红色牌可当杀使用")

        elif hero == "曹操":
            self.add_log("曹操【奸雄】已自动触发（受伤时摸牌）")

        elif hero == "司马懿":
            self.add_log("司马懿【反馈】已自动触发（受伤时摸牌）")

        elif hero == "郭嘉":
            self.add_log("郭嘉【遗计】已自动触发（受伤时摸牌）")

        self.refresh_hero_info()

    # ===================== 电脑AI =====================
    def ai_turn(self):
        self.root.update()
        time.sleep(0.8)
        self.draw_cards()
        self.root.update()
        time.sleep(0.8)

        hand = self.hands["电脑"]
        me, enemy = "电脑", "玩家"

        # 吃桃
        if self.hp[me] <= 2 and "桃" in hand:
            hand.remove("桃")
            self.hp[me] += 1
            self.add_log("电脑使用【桃】恢复血量")

        # 喝酒
        elif "酒" in hand and not self.drunk[me]:
            hand.remove("酒")
            self.drunk[me] = True
            self.add_log("电脑使用【酒】，下张杀伤害+1！")
            self.root.update()
            time.sleep(0.6)

        # 出杀
        if "杀" in hand and not self.used_slash[me]:
            self.used_slash[me] = True
            hand.remove("杀")
            dmg = 2 if self.drunk[me] else 1
            self.drunk[me] = False
            self.add_log(f"电脑对你使用【杀】，即将造成{dmg}点伤害！")
            self.root.update()
            time.sleep(0.5)
            self.enemy_dodge_check("电脑", "玩家", dmg)
            return

        self.root.update()
        time.sleep(0.8)
        self.end_turn()

    # ===================== 回合结束 =====================
    def end_turn(self):
        p = self.players[self.current_player]
        max_hand = self.hp[p]
        over = len(self.hands[p]) - max_hand
        if over > 0:
            self.hands[p] = self.hands[p][:-over]
            self.add_log(f"{p}弃掉{over}张多余手牌")

        self.used_slash[p] = False
        self.drunk[p] = False

        self.current_player = 1 - self.current_player
        self.refresh_hero_info()

        if self.current_player == 1:
            self.add_log("========== 电脑回合 ==========")
            self.disable_player_buttons()
            self.ai_turn()
        else:
            self.add_log("========== 你的回合 ==========")
            self.enable_player_buttons()

    def disable_player_buttons(self):
        self.draw_btn.config(state=tk.DISABLED)
        self.skill_btn.config(state=tk.DISABLED)
        self.end_btn.config(state=tk.DISABLED)
        for w in self.hand_frame.winfo_children():
            if isinstance(w, tk.Button):
                w.config(state=tk.DISABLED)

    def enable_player_buttons(self):
        self.draw_btn.config(state=tk.NORMAL)
        self.skill_btn.config(state=tk.NORMAL)
        self.end_btn.config(state=tk.NORMAL)
        for w in self.hand_frame.winfo_children():
            if isinstance(w, tk.Button):
                w.config(state=tk.NORMAL)

    def check_death(self):
        if self.hp["玩家"] <= 0:
            messagebox.showinfo("结束", "你阵亡了，电脑胜利！")
            self.root.quit()
        if self.hp["电脑"] <= 0:
            messagebox.showinfo("结束", "电脑阵亡，你胜利！")
            self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = SanGuoShaGame(root)
    root.mainloop()