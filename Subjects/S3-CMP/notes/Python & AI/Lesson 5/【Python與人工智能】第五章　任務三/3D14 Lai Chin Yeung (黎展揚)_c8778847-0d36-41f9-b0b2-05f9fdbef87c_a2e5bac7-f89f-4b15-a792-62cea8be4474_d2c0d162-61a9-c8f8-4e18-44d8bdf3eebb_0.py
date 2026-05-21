import tkinter as tk
from tkinter import messagebox
import random
import copy

class Xiangqi:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("中國象棋 - 完整規則 AI 對戰版")
        self.window.configure(bg="#2C3E50")
        
        self.difficulty = tk.StringVar(value="Normal")
        
        # 棋盤與 UI 尺寸
        self.cell_size = 60
        self.margin = 40
        self.width = self.cell_size * 8 + self.margin * 2
        self.height = self.cell_size * 9 + self.margin * 2
        
        # 遊戲狀態
        self.selected_pos = None
        self.player_color = 'R' # 玩家執紅 (字串開頭 R)
        self.current_turn = 'R'
        self.game_over_flag = False
        
        # 初始棋盤佈局 (r: 黑方, R: 紅方)
        self.initial_board = {
            (0,0): 'r車', (1,0): 'r馬', (2,0): 'r象', (3,0): 'r士', (4,0): 'r將', (5,0): 'r士', (6,0): 'r象', (7,0): 'r馬', (8,0): 'r車',
            (1,2): 'r砲', (7,2): 'r砲',
            (0,3): 'r卒', (2,3): 'r卒', (4,3): 'r卒', (6,3): 'r卒', (8,3): 'r卒',
            
            (0,9): 'R車', (1,9): 'R馬', (2,9): 'R相', (3,9): 'R仕', (4,9): 'R帥', (5,9): 'R仕', (6,9): 'R相', (7,9): 'R馬', (8,9): 'R車',
            (1,7): 'R砲', (7,7): 'R砲',
            (0,6): 'R兵', (2,6): 'R兵', (4,6): 'R兵', (6,6): 'R兵', (8,6): 'R兵'
        }
        self.board = copy.deepcopy(self.initial_board)
        
        self.setup_ui()
        self.draw_board()
        self.draw_pieces()

    def setup_ui(self):
        control_frame = tk.Frame(self.window, bg="#2C3E50", pady=10)
        control_frame.pack()
        
        tk.Label(control_frame, text="難度選擇:", fg="white", bg="#2C3E50", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        for text, val in [("簡單 (隨機)", "Easy"), ("普通 (貪婪)", "Normal"), ("困難 (AI)", "Hard")]:
            tk.Radiobutton(control_frame, text=text, variable=self.difficulty, value=val,
                           bg="#2C3E50", fg="#ECF0F1", selectcolor="#34495E", 
                           font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
                           
        tk.Button(control_frame, text="重新開始", bg="#E67E22", fg="white", 
                  command=self.reset_game).pack(side=tk.LEFT, padx=15)

        self.canvas = tk.Canvas(self.window, width=self.width, height=self.height, bg="#E6C28F", highlightthickness=0)
        self.canvas.pack(padx=20, pady=10)
        self.canvas.bind("<Button-1>", self.on_click)

    def draw_board(self):
        self.canvas.delete("board")
        cs, m = self.cell_size, self.margin
        for i in range(10): self.canvas.create_line(m, m + i*cs, m + 8*cs, m + i*cs, width=2)
        for i in range(9):
            if i == 0 or i == 8: self.canvas.create_line(m + i*cs, m, m + i*cs, m + 9*cs, width=2)
            else:
                self.canvas.create_line(m + i*cs, m, m + i*cs, m + 4*cs, width=2)
                self.canvas.create_line(m + i*cs, m + 5*cs, m + i*cs, m + 9*cs, width=2)
        
        self.canvas.create_line(m + 3*cs, m, m + 5*cs, m + 2*cs, width=2)
        self.canvas.create_line(m + 5*cs, m, m + 3*cs, m + 2*cs, width=2)
        self.canvas.create_line(m + 3*cs, m + 7*cs, m + 5*cs, m + 9*cs, width=2)
        self.canvas.create_line(m + 5*cs, m + 7*cs, m + 3*cs, m + 9*cs, width=2)
        
        self.canvas.create_text(m + 2*cs, m + 4.5*cs, text="楚 河", font=("楷體", 24, "bold"))
        self.canvas.create_text(m + 6*cs, m + 4.5*cs, text="漢 界", font=("楷體", 24, "bold"))

    def draw_pieces(self):
        self.canvas.delete("piece")
        cs, m, r = self.cell_size, self.margin, 22
        
        for (x, y), piece in self.board.items():
            cx, cy = m + x*cs, m + y*cs
            color = "#C0392B" if piece.startswith('R') else "#2C3E50"
            text = piece[1]
            
            self.canvas.create_oval(cx-r+2, cy-r+2, cx+r+2, cy+r+2, fill="#8B7355", outline="", tags="piece")
            self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="#FFF5E1", outline=color, width=2, tags="piece")
            self.canvas.create_text(cx, cy, text=text, font=("楷體", 20, "bold"), fill=color, tags="piece")
            
            if self.selected_pos == (x, y):
                self.canvas.create_oval(cx-r-4, cy-r-4, cx+r+4, cy+r+4, outline="#27AE60", width=3, tags="piece")

    # --- 核心：象棋走法規則判斷 ---
    
    def count_obstacles(self, start, end, board):
        x1, y1 = start
        x2, y2 = end
        count = 0
        if x1 == x2:
            step = 1 if y2 > y1 else -1
            for y in range(y1 + step, y2, step):
                if (x1, y) in board: count += 1
        else:
            step = 1 if x2 > x1 else -1
            for x in range(x1 + step, x2, step):
                if (x, y1) in board: count += 1
        return count

    def is_valid_move(self, start, end, board):
        x1, y1 = start
        x2, y2 = end
        piece = board.get(start)
        if not piece: return False
        target = board.get(end)

        # 不能吃自己的棋子
        if target and target[0] == piece[0]: return False

        p_type = piece[1]
        dx, dy = x2 - x1, y2 - y1

        if p_type in ['將', '帥']:
            if not (3 <= x2 <= 5): return False
            if piece[0] == 'R' and not (7 <= y2 <= 9): return False
            if piece[0] == 'r' and not (0 <= y2 <= 2): return False
            if abs(dx) + abs(dy) != 1: return False
            return True

        elif p_type in ['士', '仕']:
            if not (3 <= x2 <= 5): return False
            if piece[0] == 'R' and not (7 <= y2 <= 9): return False
            if piece[0] == 'r' and not (0 <= y2 <= 2): return False
            if abs(dx) != 1 or abs(dy) != 1: return False
            return True

        elif p_type in ['象', '相']:
            if piece[0] == 'R' and y2 < 5: return False # 不能過河
            if piece[0] == 'r' and y2 > 4: return False
            if abs(dx) != 2 or abs(dy) != 2: return False
            # 塞象眼檢查
            if (x1 + dx//2, y1 + dy//2) in board: return False
            return True

        elif p_type == '馬':
            if abs(dx) == 1 and abs(dy) == 2:
                if (x1, y1 + dy//2) in board: return False # 拐馬腿
                return True
            elif abs(dx) == 2 and abs(dy) == 1:
                if (x1 + dx//2, y1) in board: return False # 拐馬腿
                return True
            return False

        elif p_type == '車':
            if dx != 0 and dy != 0: return False
            return self.count_obstacles(start, end, board) == 0

        elif p_type == '砲':
            if dx != 0 and dy != 0: return False
            obstacles = self.count_obstacles(start, end, board)
            if target: return obstacles == 1 # 隔山打牛
            else: return obstacles == 0      # 平移

        elif p_type in ['兵', '卒']:
            if piece[0] == 'R': # 紅方往上走
                if dy > 0: return False
                if y1 >= 5: # 未過河
                    if dy != -1 or dx != 0: return False
                else:       # 已過河
                    if abs(dx) + abs(dy) != 1 or dy == 1: return False
            else: # 黑方往下走
                if dy < 0: return False
                if y1 <= 4: # 未過河
                    if dy != 1 or dx != 0: return False
                else:       # 已過河
                    if abs(dx) + abs(dy) != 1 or dy == -1: return False
            return True

        return False

    # --- 互動與遊戲邏輯 ---

    def on_click(self, event):
        if self.current_turn != self.player_color or self.game_over_flag: return
        
        x = round((event.x - self.margin) / self.cell_size)
        y = round((event.y - self.margin) / self.cell_size)
        
        if 0 <= x <= 8 and 0 <= y <= 9:
            clicked_piece = self.board.get((x, y))
            
            if self.selected_pos:
                if clicked_piece and clicked_piece.startswith(self.player_color):
                    self.selected_pos = (x, y) # 更換選取的棋子
                else:
                    if self.is_valid_move(self.selected_pos, (x, y), self.board):
                        self.execute_move(self.selected_pos, (x, y))
                        self.selected_pos = None
                        self.draw_pieces()
                        if not self.game_over_flag:
                            self.current_turn = 'r'
                            self.window.after(300, self.ai_turn)
            else:
                if clicked_piece and clicked_piece.startswith(self.player_color):
                    self.selected_pos = (x, y)
            self.draw_pieces()

    def execute_move(self, start, end):
        piece = self.board.pop(start)
        target = self.board.get(end)
        if target:
            if target == 'r將': self.game_over("玩家 (紅方)")
            elif target == 'R帥': self.game_over("電腦 (黑方)")
            
        self.board[end] = piece

    def game_over(self, winner):
        self.game_over_flag = True
        messagebox.showinfo("遊戲結束", f"{winner} 獲勝！")

    def reset_game(self):
        self.board = copy.deepcopy(self.initial_board)
        self.current_turn = 'R'
        self.selected_pos = None
        self.game_over_flag = False
        self.draw_pieces()

    # --- AI 決策系統 ---
    
    def get_legal_moves(self, is_red=False):
        """根據真實規則產生合法步數"""
        moves = []
        prefix = 'R' if is_red else 'r'
        for (x, y), piece in list(self.board.items()):
            if piece.startswith(prefix):
                for nx in range(9):
                    for ny in range(10):
                        if self.is_valid_move((x, y), (nx, ny), self.board):
                            moves.append(((x, y), (nx, ny)))
        return moves

    def evaluate_board(self):
        values = {'車': 90, '馬': 40, '砲': 45, '象': 20, '相': 20, '士': 20, '仕': 20, '卒': 10, '兵': 10, '將': 10000, '帥': 10000}
        score = 0
        for piece in self.board.values():
            val = values.get(piece[1], 0)
            score += val if piece.startswith('r') else -val
        return score

    def ai_turn(self):
        if self.current_turn != 'r' or self.game_over_flag: return
        
        diff = self.difficulty.get()
        moves = self.get_legal_moves(is_red=False)
        if not moves: 
            self.game_over("玩家 (紅方)") # 電腦無步可走被將死
            return
            
        best_move = None
        
        if diff == "Easy":
            best_move = random.choice(moves)
            
        elif diff == "Normal":
            best_score = -1
            best_move = random.choice(moves)
            for start, end in moves:
                target = self.board.get(end)
                if target:
                    val = {'車':90, '馬':40, '砲':45, '相':20, '仕':20, '兵':10, '帥':10000}.get(target[1], 0)
                    if val > best_score:
                        best_score = val
                        best_move = (start, end)
                        
        else: # Hard: 淺層 Minimax
            best_eval = -float('inf')
            best_move = random.choice(moves)
            # 隨機打亂避免每次走法一樣
            random.shuffle(moves) 
            for start, end in moves:
                piece = self.board.pop(start)
                target = self.board.get(end)
                self.board[end] = piece
                
                current_eval = self.evaluate_board()
                if current_eval > best_eval:
                    best_eval = current_eval
                    best_move = (start, end)
                
                self.board[start] = piece
                if target: self.board[end] = target
                else: del self.board[end]

        if best_move:
            self.execute_move(best_move[0], best_move[1])
        
        if not self.game_over_flag:
            self.current_turn = 'R'
            self.draw_pieces()

if __name__ == "__main__":
    Xiangqi().window.mainloop()