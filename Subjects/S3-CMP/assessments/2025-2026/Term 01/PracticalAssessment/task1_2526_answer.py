# Input
name = input("Traveller name: ")
transport = int(input("Transport: "))
hotel = int(input("Hotel: "))
food = int(input("Food: "))

# Calculations
total = transport + hotel + food
avg = total / 3

# Decide grade and remark
if avg >= 1500:
    grade = "A"
    remark = "Luxury trip"
elif avg >= 800:
    grade = "B"
    remark = "Standard trip"
else:
    grade = "C"
    remark = "Budget trip"

# Output
print("Total =", total)
print("Average =", round(avg, 1))
print("Grade:", grade)
print("Remark:", remark)
