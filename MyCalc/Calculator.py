class Calculator:
    answer = 0

    def __init__(self):
        pass

    @classmethod
    def add(cls, num):
        cls.answer += num
        return round(cls.answer,6)

    @classmethod
    def subtract(cls, num):
        cls.answer -= num
        return cls.answer

    @classmethod
    def multiply(cls, num):
        cls.answer *= num
        return cls.answer

    @classmethod
    def divide(cls, num):
        try:
            cls.answer /= num
            return cls.answer
        except ZeroDivisionError:
            print("divide by zero")

    @classmethod
    def get_answer(cls):
        return cls.answer

    @classmethod
    def reset(cls):
        cls.clear()

    @classmethod
    def clear(cls):
        cls.answer = 0
        return cls.answer


if __name__ == "__main__":
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
        num = float(input("Enter number:"))
        if choice == "1":
            print(Calculator.answer, "+", num, "=", Calculator.add(num))
        elif choice == "2":
            print(Calculator.answer, "-", num, "=", Calculator.subtract(num))
        elif choice == "3":
            print(Calculator.answer, "*", num, "=", Calculator.multiply(num))
        elif choice == "4":
            print(Calculator.answer, "/", num, "=", Calculator.divide(num))
        else:
            print("Invalid choice")
