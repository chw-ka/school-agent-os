balance = 500
print("Initial balance = $" + str(balance))

while True:
    price = int(input("Enter item price (0 to exit): "))

    if price == 0:
        # Exit the loop
        break
    elif price < 0 or price % 5 != 0:
        print("Invalid price! Must be positive and in $5 units.")
    elif price > balance:
        print("Not enough balance!")
    else:
        balance = balance - price
        print("Purchase successful. New balance = $" + str(balance))

print("Final balance = $" + str(balance))
