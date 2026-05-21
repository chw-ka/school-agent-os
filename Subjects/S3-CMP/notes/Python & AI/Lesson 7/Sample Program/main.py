import tkinter as tk
from tkinter import messagebox
import json
import random

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python 隨機測驗系統")
        self.root.geometry("500x400")

        # 初始化變數
        self.questions = self.load_data()
        random.shuffle(self.questions) # 隨機出題
        self.current_idx = 0
        self.score = 0
        self.user_results = [] # 紀錄每題對錯

        self.setup_ui()
        self.display_question()

    def load_data(self):
        """從 JSON 檔案讀取題目"""
        try:
            with open("quiz_data.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            messagebox.showerror("錯誤", "找不到 quiz_data.json 檔案！")
            self.root.destroy()
            return []

    def setup_ui(self):
        """初始化 UI 元件"""
        # 題目顯示區
        self.question_label = tk.Label(self.root, text="", font=("Arial", 14), wraplength=400, pady=20)
        self.question_label.pack()

        # 選項按鈕區
        self.option_buttons = []
        for i in range(4):
            btn = tk.Button(self.root, text="", font=("Arial", 12), width=30, height=2,
                            command=lambda i=i: self.check_answer(i))
            btn.pack(pady=5)
            self.option_buttons.append(btn)

        # 進度顯示
        self.progress_label = tk.Label(self.root, text="", font=("Arial", 10), fg="gray")
        self.progress_label.pack(side="bottom", pady=10)

    def display_question(self):
        """將題目與選項載入介面"""
        if self.current_idx < len(self.questions):
            q_data = self.questions[self.current_idx]
            self.question_label.config(text=f"Q{self.current_idx + 1}: {q_data['question']}")
            
            # 更新按鈕文字
            for i, option in enumerate(q_data['options']):
                self.option_buttons[i].config(text=option, state="normal")
            
            self.progress_label.config(text=f"進度: {self.current_idx + 1} / {len(self.questions)}")
        else:
            self.show_final_results()

    def check_answer(self, selected_idx):
        """檢查答案並紀錄結果"""
        q_data = self.questions[self.current_idx]
        selected_text = self.option_buttons[selected_idx].cget("text")
        correct_answer = q_data['answer']

        is_correct = (selected_text == correct_answer)
        if is_correct:
            self.score += 1
        
        # 儲存紀錄供最後成績單使用
        self.user_results.append({
            "q": q_data['question'],
            "user": selected_text,
            "correct": correct_answer,
            "res": "O" if is_correct else "X"
        })

        # 自動跳轉下一題
        self.current_idx += 1
        self.display_question()

    def show_final_results(self):
        """顯示最終成績單"""
        # 清除所有按鈕
        for btn in self.option_buttons:
            btn.pack_forget()
        
        self.question_label.config(text=f"測驗結束！總分: {self.score} / {len(self.questions)}", fg="blue")

        # 建立成績列表文字
        report = "--- 詳細成績單 ---\n\n"
        for i, item in enumerate(self.user_results):
            report += f"{i+1}. {item['res']} | 題目: {item['q']}\n"
            if item['res'] == "X":
                report += f"   (你的答案: {item['user']} / 正確: {item['correct']})\n"
        
        # 使用滾動文字框顯示詳細結果
        result_text = tk.Text(self.root, height=10, width=55, font=("Arial", 10))
        result_text.insert(tk.END, report)
        result_text.config(state="disabled") # 唯讀
        result_text.pack(pady=10)

        # 關閉按鈕
        exit_btn = tk.Button(self.root, text="結束程式", command=self.root.quit)
        exit_btn.pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()