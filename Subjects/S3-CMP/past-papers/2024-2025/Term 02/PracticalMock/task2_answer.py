numbers = []
while True:
    num = int(input("Enter a number (or -1 to stop): "))
    if num == -1:
        break
    elif  num > 0:
        numbers.append(num)
    else:
        print(num ,"is lower than 0.")

print("Positive numbers:", numbers)
