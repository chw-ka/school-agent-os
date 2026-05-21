import time

def clear_screen():
    print("\n" * 5)

# --- 1. 堆疊 Stack (LIFO) ---
def stack_demo():
    stack = []
    while True:
        clear_screen()
        print(f"=== 堆疊 Stack (後進先出 LIFO) ===\n目前狀態: {stack} <--- 頂部 (Top)")
        print("1. Push (推入)  2. Pop (彈出)  3. 返回")
        choice = input("請選擇: ")
        if choice == '1':
            item = input("輸入要加入的資料: ")
            stack.append(item)
        elif choice == '2':
            if stack:
                print(f"彈出資料: {stack.pop()}")
                time.sleep(1)
            else:
                print("錯誤：堆疊已空！")
                time.sleep(1)
        elif choice == '3': break

# --- 2. 隊列 Queue (FIFO) ---
def queue_demo():
    queue = []
    while True:
        clear_screen()
        print(f"=== 隊列 Queue (先進先出 FIFO) ===\n目前狀態: {queue}")
        print("1. Enqueue (排隊)  2. Dequeue (出隊)  3. 返回")
        choice = input("請選擇: ")
        if choice == '1':
            item = input("輸入要加入的資料: ")
            queue.append(item)
        elif choice == '2':
            if queue:
                print(f"移出資料: {queue.pop(0)}")
                time.sleep(1)
            else:
                print("錯誤：隊列已空！")
                time.sleep(1)
        elif choice == '3': break

# --- 3. 連結表 Linked List (概念模擬) ---
def linked_list_demo():
    nodes = ["Head"]
    while True:
        clear_screen()
        display = " -> ".join([f"[{n}]" for n in nodes]) + " -> None"
        print(f"=== 連結表 Linked List ===\n結構展示: {display}")
        print("1. 新增節點 (尾部)  2. 刪除最後節點  3. 返回")
        choice = input("請選擇: ")
        if choice == '1':
            item = input("輸入節點內容: ")
            nodes.append(item)
        elif choice == '2':
            if len(nodes) > 1:
                nodes.pop()
            else:
                print("只剩 Head 節點，不可刪除！")
                time.sleep(1)
        elif choice == '3': break

# 主程式選單
def main():
    while True:
        clear_screen()
        print("【數據結構自我學習工具】")
        print("1. 學習 Stack")
        print("2. 學習 Queue")
        print("3. 學習 Linked List")
        print("4. 退出")
        cmd = input("請選擇學習主題: ")
        if cmd == '1': stack_demo()
        elif cmd == '2': queue_demo()
        elif cmd == '3': linked_list_demo()
        elif cmd == '4': break

if __name__ == "__main__":
    main()