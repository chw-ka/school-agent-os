# (b) 一開始設定帳戶結餘

print("Initial balance = $" + str(balance))

# (c) 程式可以 不斷購物，直到使用者輸入 0 結束 (while)

    price = int(input("Enter item price (0 to exit): "))

# (d) 每次輸入後要進行檢查：
    
        

    
        print("Invalid price! Must be positive and in $5 units.")
        continue
    

        print("Not enough balance!")
        continue


    balance = balance - price
    print("Purchase successful. New balance = $" + str(balance))

# (e) 當使用者輸入 0 結束時，最後輸出：
