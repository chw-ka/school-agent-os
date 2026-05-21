# part (b) line 2
name_list = 

while True:
    print("\nChoose a mode:")
    print("1. Add a student name")
    print("2. Remove a student name")
    print("3. Insert a name at the beginning")
    print("4. Show all names and long names")
    print("5. Quit")
    mode = input("Select 1-5: ")

    if mode == "1":
        # part (c) line 16
        name = input("Enter a student name to add: ")
        name_list.

    elif mode == "2":
        # part (d) line 22
        name = input("Enter a student name to remove: ")
        if name in name_list:
            name_list.
            print(name, "removed.")
        else:
            print("Name not found.")

    elif mode == "3":
        # part (e) line 30
        name = input("Enter a name to insert at the beginning: ")
        name_list.

    elif mode == "4":
        # part (f) line 36 - 37
        long_names = []
        for name in name_list:
            if 
                long_names.
        print("All names:", name_list)
        print("Names longer than 5 characters:", long_names)

    elif mode == "5":
        print("Goodbye!")
        break

    else:
        print("Invalid option. Please select 1-5.")