import random

print("=== Lucky Number Battle ===")
print("You and the CPU will pick a number 5 times.")

user_score = 0
cpu_score = 0

for round_num in range(1, 6):
    print("Round", round_num)
    input("Press Enter to draw a number...")

    user_num = random.randint(1, 10)
    cpu_num = random.randint(1, 10)

    print("You got", user_num, ", CPU got", cpu_num)

    if user_num > cpu_num:
        print("You win this round!")
        user_score += 1

        # Extra requirement: big difference
        if user_num - cpu_num >= 3:
            print("Great win!")
    elif user_num < cpu_num:
        print("CPU wins this round!")
        cpu_score = cpu_score + 1
    else:
        print("This round is a draw.")

# Final result
print("Final score: You", user_score, ":", cpu_score, "CPU")

if user_score > cpu_score:
    print("You win the game!")
elif user_score < cpu_score:
    print("CPU wins the game!")
else:
    print("It's a draw!")
