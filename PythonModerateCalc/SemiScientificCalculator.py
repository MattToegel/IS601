from PythonModerateCalc import Calculator
import csv
from array import array


class SemiScientificCalculator(Calculator):

    def __init__(self):
        pass

    @classmethod
    def pow(cls, num):
        cls.answer = pow(cls.answer, num)
        return cls.answer

    def mean(*num):
        c = len(num)
        return sum(num) / c


if __name__ == "__main__":
    # Don't copy this, it's not very clean...at all
    choice = ""
    while choice != "quit":
        print("Select operation.")
        print("1.Add")
        print("2.Subtract")
        print("3.Multiply")
        print("4.Divide")
        print("5.Pow")
        print("6.Mean")
        print("7.Mean (Imported)")
        choice = input("Enter choice:")
        if int(choice) <= 5:
            num = float(input("Enter number:"))
        if choice == "quit":
            break

        if choice == "1":
            print(SemiScientificCalculator.answer, "+", num, "=", SemiScientificCalculator.add(num))
        elif choice == "2":
            print(SemiScientificCalculator.answer, "-", num, "=", SemiScientificCalculator.subtract(num))
        elif choice == "3":
            print(SemiScientificCalculator.answer, "*", num, "=", SemiScientificCalculator.multiply(num))
        elif choice == "4":
            print(SemiScientificCalculator.answer, "/", num, "=", SemiScientificCalculator.divide(num))
        elif choice == "5":
            print(SemiScientificCalculator.answer, "^", num, "=", SemiScientificCalculator.pow(num))
        elif choice == "6":
            num2 = input("Enter a list of numbers: ")
            num2 = [float(i) for i in num2.split()]
            print(SemiScientificCalculator.mean(*num2))
        elif choice == "7":
            with open("meanlist.csv", newline='') as csvfile:
                nums = list(csv.reader(csvfile))
            # print(nums)
            for l in nums:
                n = [float(i) for i in l]
                print([str(i) for i in n], "=", SemiScientificCalculator.mean(*n))
            # print(num, "X̄", num2, "=", SemiScientificCalculator.mean(num, num2))
        else:
            print("Invalid choice")
