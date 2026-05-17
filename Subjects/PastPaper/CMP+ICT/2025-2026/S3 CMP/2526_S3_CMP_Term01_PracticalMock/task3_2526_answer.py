import random

print("=== Dice Battle Game ===")
print("You and the CPU will roll a dice 5 times.\n")

user_score = 0
cpu_score = 0

for round_no in range(1, 6):
    print("Round", round_no)
    input("Press Enter to roll...")

    user_dice = random.randint(1, 6)
    cpu_dice = random.randint(1, 6)

    print("You rolled", user_dice, ", CPU rolled", cpu_dice)

    if user_dice > cpu_dice:
        print("You win this round!")
        user_score += 1
        if user_dice - cpu_dice >= 3:
            print("Big win!")
    elif user_dice < cpu_dice:
        print("CPU wins this round!")
        cpu_score += 1
    else:
        print("This round is a draw.")

    print()  # 空行分隔回合

print("Final score: You", user_score, ":", cpu_score, "CPU")

if user_score > cpu_score:
    print("You win the game!")
elif user_score < cpu_score:
    print("CPU wins the game!")
else:
    print("It's a draw!")