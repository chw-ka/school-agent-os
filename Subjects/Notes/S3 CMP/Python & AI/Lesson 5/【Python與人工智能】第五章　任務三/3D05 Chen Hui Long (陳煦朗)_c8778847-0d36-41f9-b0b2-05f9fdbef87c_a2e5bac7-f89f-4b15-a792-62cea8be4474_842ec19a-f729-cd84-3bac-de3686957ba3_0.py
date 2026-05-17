import time
import random
import sys

def print_ui(score, combo, time_left, question=""):
    """繪製美化的遊戲界面"""
    sys.stdout.write("\033[H\033[J") # 清除屏幕
    print("=" * 40)
    print(f"🔥 3X99: 極速連擊 🔥".center(40))
    print("=" * 40)
    print(f"分數: {score} | 連擊: x{combo} | 時間: {time_left:.1f}s")
    print("-" * 40)
    if question:
        print(f"\n題目： {question} = ?\n")
    print("-" * 40)

def game_loop():
    score = 0
    combo = 0
    base_time = 5.0
    
    print("\n[ 遊戲規則 ]")
    print("1. 快速回答乘法題")
    print("2. 連續答對分數翻倍")
    print("3. 時間用盡或答錯則結束")
    input("\n按 Enter 開始挑戰...")

    while True:
        a, b = random.randint(2, 9), random.randint(2, 9)
        answer = a * b
        question = f"{a} x {b}"
        
        # 動態調整難度：每 500 分減少一點基礎時間
        time_limit = max(1.5, base_time - (score // 500) * 0.5)
        
        print_ui(score, combo, time_limit, question)
        
        start_time = time.time()
        user_input = input("回答: ")
        end_time = time.time()
        
        elapsed = end_time - start_time
        
        # 判斷邏輯
        if user_input.isdigit() and int(user_input) == answer and elapsed <= time_limit:
            combo += 1
            # 獎勵分數 = (基礎分 + 剩餘時間獎金) * 連擊倍率
            added_score = int((10 + (time_limit - elapsed) * 10) * combo)
            score += added_score
            print(f"\n✅ 太棒了！ +{added_score}")
            print("\a") # 系統蜂鳴聲 (音效元素)
            time.sleep(0.3)
        else:
            print_ui(score, combo, 0, question)
            print("\n❌ 遊戲結束！")
            if elapsed > time_limit:
                print("原因：超時了！")
            else:
                print(f"原因：答錯了！正確答案是 {answer}")
            
            print(f"\n最終得分: {score}")
            print(f"最高連擊: {combo}")
            break

if __name__ == "__main__":
    try:
        game_loop()
    except KeyboardInterrupt:
        print("\n遊戲已退出。")