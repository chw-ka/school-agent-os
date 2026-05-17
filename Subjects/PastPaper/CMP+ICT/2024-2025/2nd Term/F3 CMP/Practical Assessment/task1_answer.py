# Calculate BMI
weight = int(input("Enter your weight in kg: "))
height = float(input("Enter your height in meters: "))
bmi = weight / (height ** 2)
print("Your BMI is: " + str(bmi))