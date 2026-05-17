scores = []
while True:
    num = int(input("Enter a number (or -1 to stop): "))
    if num == -1:
        break
    elif num >= 0:
        scores.append(num)
    else:
        print(str(num) + " is lower than 0.")

max_score = max(scores)
min_score = min(scores)
average_score = sum(scores) / len(scores)
print("The maximum score is: " + str(max_score))
print("The minimum score is: " + str(min_score))
print("The average score is: " + str(average_score))
