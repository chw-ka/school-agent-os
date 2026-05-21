# Task3_3X99.py
# 《節奏光劍 · 音速反擊》
# 一個結合節奏、連擊、壓力的街機風格反應遊戲

import random
import time
import sys
import os

# 全域變數
score = 0
combo = 0
combo_multiplier = 1
time_left = 3.0
powerup_active = False
powerup_type = None
powerup_remaining = 0

def clear_screen():
    """清空畫面（跨平台）"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """顯示遊戲標題"""
    banner = """
    ╔══════════════════════════════════════╗
    ║     🎵  節奏光劍 · 音速反擊  🎵      ║
    ║         Rhythm Saber Strike          ║
    ╚══════════════════════════════════════╝
    """
    print(banner)

def print_instructions():
    """顯示操作說明"""
    print("\n🎮 遊戲規則：")
    print("  → 目標會從左向右移動")
    print("  → 當目標到達【★】時，按下對應數字鍵")
    print("\n⌨️  按鍵：")
    print("  1 → 左  2 → 中  3 → 右")
    print("  q → 離開遊戲")
    print("\n✨ 連擊倍率：1x → 2x → 3x → 5x")
    print("💥 連續命中會增加速度與分數！")
    input("\n按 Enter 開始遊戲...")

def spawn_target():
    """生成一個目標"""
    lanes = ['←', '↑', '→']
    lane_index = random.randint(0, 2)
    target_symbol = lanes[lane_index]
    # 距離（步數），越大越難
    distance = random.randint(3, 6)
    return {
        'lane': lane_index,
        'symbol': target_symbol,
        'position': 0,  # 0 = 最左, distance = 到達★
        'max_pos': distance
    }

def draw_lane(target, current_pos, lane_width=10):
    """繪製單一跑道"""
    lane_art = [" " for _ in range(lane_width)]
    # 目標位置
    if target and current_pos < len(lane_art):
        lane_art[current_pos] = target['symbol']
    # 打擊點★
    lane_art[lane_width - 2] = "★"
    return "".join(lane_art)

def display_game(targets, score, combo, multiplier, time_left, powerup_msg=""):
    """顯示遊戲畫面"""
    clear_screen()
    print_banner()
    print(f"\n🎯 分數: {score}   |   🔥 連擊: {combo}   |   ✨ 倍率: {multiplier}x")
    print(f"⏱️  剩餘時間: {time_left:.1f} 秒")
    if powerup_msg:
        print(f"✨ {powerup_msg}")
    print("\n" + "="*40)
    
    # 繪製三個跑道
    lanes_display = ["左", "中", "右"]
    for i in range(3):
        target = next((t for t in targets if t['lane'] == i), None)
        if target:
            pos = min(target['position'], 8)
        else:
            pos = -1
        lane_str = draw_lane(target, pos)
        print(f"{lanes_display[i]} | {lane_str}")
    
    print("="*40)
    print("          1      2      3")
    print("         ←      ↑      →")

def update_targets(targets, speed):
    """更新目標位置，回傳是否有人到達終點"""
    to_remove = []
    for target in targets:
        target['position'] += speed
        if target['position'] >= target['max_pos']:
            to_remove.append(target)
    
    for t in to_remove:
        targets.remove(t)
    
    # 如果有目標到達終點，表示失誤
    return len(to_remove) > 0

def apply_powerup(powerup_type):
    """套用強化道具效果"""
    global combo_multiplier, time_left, combo
    if powerup_type == "double":
        combo_multiplier = min(combo_multiplier * 2, 5)
        return "分數倍率提升！"
    elif powerup_type == "freeze":
        return "時間凍結 2 秒！"
    elif powerup_type == "shield":
        combo = max(0, combo - 2)
        return "失誤保護！連擊減少減少"
    return ""

def game_loop():
    """主遊戲迴圈"""
    global score, combo, combo_multiplier, time_left, powerup_active, powerup_type, powerup_remaining
    
    # 遊戲狀態
    targets = []
    game_over = False
    speed = 0.4  # 移動速度
    spawn_timer = 0
    last_time = time.time()
    frozen_time = 0
    
    # 生成第一個目標
    targets.append(spawn_target())
    
    while not game_over:
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time
        
        # 處理時間凍結
        if frozen_time > 0:
            frozen_time -= dt
            dt = 0
        
        # 倒數計時
        if not powerup_active or powerup_type != "freeze":
            time_left -= dt
            if time_left <= 0:
                game_over = True
                break
        
        # 更新目標位置
        miss = update_targets(targets, speed * dt * 2)
        if miss:
            # 失誤懲罰
            combo = 0
            combo_multiplier = 1
            time_left -= 0.5
            print("\n💔 MISS！連擊中斷")
            time.sleep(0.3)
        
        # 生成新目標（隨機計時）
        spawn_timer += dt
        if spawn_timer > random.uniform(0.6, 1.2) and len(targets) < 5:
            targets.append(spawn_target())
            spawn_timer = 0
        
        # 隨機生成強化道具（低機率）
        if random.random() < 0.02 and not powerup_active:
            powerup_type = random.choice(["double", "freeze", "shield"])
            powerup_active = True
            powerup_remaining = 5
            msg = apply_powerup(powerup_type)
            display_game(targets, score, combo, combo_multiplier, time_left, msg)
            time.sleep(1)
        
        # 處理強化道具剩餘時間
        if powerup_active:
            powerup_remaining -= dt
            if powerup_remaining <= 0:
                powerup_active = False
                powerup_type = None
        
        # 顯示畫面
        display_game(targets, score, combo, combo_multiplier, time_left)
        
        # 處理輸入（非阻塞式）
        import select
        import sys
        
        # 檢查是否有輸入
        if select.select([sys.stdin], [], [], 0.1)[0]:
            key = sys.stdin.read(1).lower()
            
            if key == 'q':
                game_over = True
                break
            
            # 檢查數字鍵 1,2,3
            if key in ['1', '2', '3']:
                lane_index = int(key) - 1
                hit = False
                for target in targets[:]:
                    if target['lane'] == lane_index and target['position'] >= target['max_pos'] - 1:
                        # 命中！
                        targets.remove(target)
                        hit = True
                        # 計算分數（距離打擊點越近分數越高）
                        distance_to_target = abs(target['position'] - target['max_pos'])
                        if distance_to_target < 0.5:
                            points = 100
                            perfect = True
                        elif distance_to_target < 1.2:
                            points = 50
                            perfect = False
                        else:
                            points = 30
                            perfect = False
                        
                        # 套用倍率
                        add_score = points * combo_multiplier
                        score += add_score
                        
                        # 增加連擊
                        combo += 1
                        if combo >= 5:
                            combo_multiplier = 3
                        elif combo >= 10:
                            combo_multiplier = 5
                        elif combo >= 3:
                            combo_multiplier = 2
                        
                        # 動態難度：速度隨連擊增加
                        speed = min(0.4 + combo * 0.02, 1.2)
                        
                        # 顯示命中效果
                        if perfect:
                            print(f"\n🎯 PERFECT! +{add_score} (x{combo_multiplier})")
                        else:
                            print(f"\n⚡ HIT! +{add_score} (x{combo_multiplier})")
                        
                        # 命中後加一點時間
                        time_left = min(time_left + 0.2, 4.0)
                        
                        time.sleep(0.05)
                        break
                
                if not hit:
                    # 打錯目標
                    combo = 0
                    combo_multiplier = 1
                    time_left -= 0.3
                    print("\n❌ 打錯位置！")
                    time.sleep(0.2)
    
    return score

def show_game_over(final_score):
    """顯示遊戲結束畫面"""
    clear_screen()
    print_banner()
    print("\n" + "="*40)
    print("          GAME OVER")
    print("="*40)
    print(f"\n🎉 最終分數：{final_score}")
    
    # 評級
    if final_score >= 5000:
        grade = "SSS 節奏之神！"
    elif final_score >= 3000:
        grade = "S 超強節奏感！"
    elif final_score >= 1500:
        grade = "A 不錯喔！"
    elif final_score >= 500:
        grade = "B 再練一下"
    else:
        grade = "C 再試一次吧"
    
    print(f"🏆 評級：{grade}")
    
    # 高分成績（簡單存檔）
    try:
        with open("highscore.txt", "r") as f:
            highscore = int(f.read())
    except:
        highscore = 0
    
    if final_score > highscore:
        print(f"✨ 新紀錄！超越舊紀錄 {highscore} 分")
        with open("highscore.txt", "w") as f:
            f.write(str(final_score))
    else:
        print(f"📊 最高紀錄：{highscore} 分")
    
    print("\n")

def main():
    """主程式"""
    while True:
        clear_screen()
        print_banner()
        print_instructions()
        
        # 執行遊戲
        final_score = game_loop()
        
        # 顯示結果
        show_game_over(final_score)
        
        # 詢問是否再玩
        again = input("再玩一次？(y/n): ").lower()
        if again != 'y':
            print("\n感謝遊玩《節奏光劍》！👋")
            break

if __name__ == "__main__":
    main()