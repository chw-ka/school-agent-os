import random

# 枪械基类（父类）
class Gun:
    def __init__(self, name, damage, ammo, range_bonus):
        self.name = name  # 枪名
        self.damage = damage  # 基础伤害
        self.ammo = ammo  # 总子弹数
        self.range_bonus = range_bonus  # 距离加成（影响伤害）

    # 射击方法
    def shoot(self):
        if self.ammo <= 0:
            print(f"【{self.name}】没有子弹了！无法射击！")
            return 0

        # 基础伤害 + 随机浮动 + 距离加成
        final_damage = random.randint(int(self.damage * 0.8), int(self.damage * 1.2)) + self.range_bonus
        self.ammo -= 1
        print(f"你使用【{self.name}】射击，造成了 {final_damage} 点伤害！剩余子弹：{self.ammo}")
        return final_damage

    # 换弹
    def reload(self, max_ammo):
        self.ammo = max_ammo
        print(f"【{self.name}】已换弹！子弹恢复满：{self.ammo}")

# 突击步枪
class AssaultRifle(Gun):
    def __init__(self):
        super().__init__(name="突击步枪", damage=30, ammo=30, range_bonus=5)
        self.max_ammo = 30

# 狙击枪
class SniperRifle(Gun):
    def __init__(self):
        super().__init__(name="狙击枪", damage=80, ammo=5, range_bonus=20)
        self.max_ammo = 5

# 手枪
class Pistol(Gun):
    def __init__(self):
        super().__init__(name="手枪", damage=15, ammo=12, range_bonus=0)
        self.max_ammo = 12

# 敌人类
class Enemy:
    def __init__(self):
        self.hp = 200  # 敌人血量

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
        print(f"敌人剩余血量：{self.hp}")

# 游戏主程序
def game():
    print("===== Python 枪战游戏 =====")
    print("1. 突击步枪")
    print("2. 狙击枪")
    print("3. 手枪")

    # 选择武器
    while True:
        choice = input("请选择你的枪械（输入数字）：")
        if choice == "1":
            player_gun = AssaultRifle()
            break
        elif choice == "2":
            player_gun = SniperRifle()
            break
        elif choice == "3":
            player_gun = Pistol()
            break
        else:
            print("输入错误，请重新选择！")

    enemy = Enemy()
    print(f"\n你选择了：{player_gun.name}，敌人已出现！")
    print("游戏指令：shoot（射击）、reload（换弹）、exit（退出）\n")

    # 游戏循环
    while True:
        if enemy.hp <= 0:
            print("\n🎉 恭喜！你击败了敌人！游戏胜利！")
            break

        cmd = input("请输入指令：").strip().lower()

        if cmd == "shoot":
            damage = player_gun.shoot()
            if damage > 0:
                enemy.take_damage(damage)

        elif cmd == "reload":
            player_gun.reload(player_gun.max_ammo)

        elif cmd == "exit":
            print("退出游戏")
            break

        else:
            print("无效指令！可用：shoot / reload / exit")

# 启动游戏
if __name__ == "__main__":
    game()