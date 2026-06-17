# (b) 一開始設定帳戶結餘

print("Initial balance = $" + str(balance))

# (c) 程式可以 不斷提款，直到使用者輸入 0 結束 (while)

    amt = int(input("Enter amount to withdraw (0 to exit): "))

# (d) 每次輸入後要進行檢查：
    
        

    
        print("Invalid amount! Must be positive and in 100s.")
        continue
    

        print("Not enough balance!")
        continue


    balance -= amt
    print("Withdrawal successful. New balance = $" + str(balance))

# (e) 當使用者輸入 0 結束時，最後輸出：
