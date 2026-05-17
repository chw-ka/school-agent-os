balance = 2000
print("Initial balance = $" + str(balance))

while True:
    amt = int(input("Enter amount to withdraw (0 to exit): "))

    if amt == 0:
        break

    if amt <= 0 or amt % 100 != 0:
        print("Invalid amount! Must be positive and in 100s.")
        continue
    if amt > balance:
        print("Not enough balance!")
        continue
    balance -= amt
    print("Withdrawal successful. New balance = $" + str(balance))

print("Final balance = $" + str(balance))