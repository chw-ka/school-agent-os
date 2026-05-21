# Task3_3X99.py  閃電數字挑戰 - 最受歡迎遊戲
import random
import time

def game_start():
    # 遊戲初始化參數
    score = 0  # 總分數
    combo = 0  # 連擊數
    max_combo = 0  # 最高連擊
    time_limit = 7  # 每題限時3秒
    5
    5
    
    level = 1  # 關卡數

    print("=" * 40)
    print("🎮 歡迎來到【閃電數字挑戰】🎮")
    print("規則：輸入題目答案，3秒內答對得分！")
    print("✨ 連擊越多，分數加倍越高 ✨")
    print("=" * 40)
    input("按Enter開始遊戲！")

    # 無限遊戲循環
    while True:
        # 隨機生成加法/減法題目（適合新手的簡單題目）
        num1 = random.randint(1, 20)
        num2 = random.randint(1, 20)
        op = random.choice(["+", "-"])

        # 計算正確答案（減法保證結果非負數）
        if op == "-":
            if num1 < num2:
                num1, num2 = num2, num1
            answer = num1 - num2
        else:
            answer = num1 + num2

        # 顯示題目與關卡資訊
        print(f"\n📌 第{level}關 | 當前連擊：{combo} | 總分：{score}")
        print(f"⏰ 限時{time_limit}秒 → 題目：{num1} {op} {num2} = ?")

        # 記錄答題開始時間
        start_time = time.time()

        # 接收玩家答案
        try:
            user_ans = int(input("請輸入答案："))
        except ValueError:
            user_ans = -1  # 輸入非數字直接判定錯誤

        # 計算答題耗時
        use_time = time.time() - start_time

        # 判斷答題結果
        if user_ans == answer and use_time <= time_limit:
            # 答對：連擊+1，計算加倍分數
            combo += 1
            max_combo = max(max_combo, combo)
            # 連擊加倍：最高5倍
            multiple = min(combo, 5)
            add_score = 10 * multiple
            score += add_score
            print(f"✅ 正確！+{add_score}分 (×{multiple}倍)")
            level += 1  # 關卡+1
        else:
            # 答錯/超時：連擊重置
            combo = 0
            if use_time > time_limit:
                print("❌ 時間到！挑戰失敗")
            else:
                print(f"❌ 答錯了！正確答案：{answer}")
            # 遊戲結束
            print("\n" + "=" * 40)
            print("🎯 遊戲結束！最終成績")
            print(f"🏆 總分：{score}")
            print(f"🔥 最高連擊：{max_combo}")
            print(f"📊 通關數：{level-1}關")
            print("=" * 40)
            break

# 啟動遊戲
if __name__ == "__main__":
    game_start()