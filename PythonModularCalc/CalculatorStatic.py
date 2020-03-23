class CalculatorStatic:
    answer = 0

    def __init__(self):
        pass
        
    @staticmethod
    def add(num1, num2):
        return num1 + num2

    @staticmethod
    def subtract(num1, num2):
        return num1 - num2

    @staticmethod
    def multiply(num1, num2):
        return num1 * num2

    @staticmethod
    def divide(num1, num2):
        return num1 / num2

if __name__ == "__main__":
    #c = Calculator()
    choice = ""
    while choice != "quit":
        print("Select operation.")
        print("1.Add")
        print("2.Subtract")
        print("3.Multiply")
        print("4.Divide")
        print("5. Quit")
        choice = input("Enter choice:")
        if choice == "5" or choice == "quit":
           break
        num1 = float(input("Enter a number:"))
        num2 = float(input("Enter a second number:"))
        if choice == "1":
            print(num1, "+", num2, "=", Calculator.add(num1, num2))
        elif choice == "2":
            print(num1, "-", num2, "=", Calculator.subtract(num1, num2))
        elif choice == "3":
            print(num1, "*", num2, "=", Calculator.multiply(num1, num2))
        elif choice == "4":
            print(num1, "/", num2, "=", Calculator.divide(num1, num2))
        else:
            print("Invalid choice")
