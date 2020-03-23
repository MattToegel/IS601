from Modules.add import *
from Modules.subtract import *
from Modules.multiply import *
from Modules.divide import *
from Modules.Answer import *


class Calculator(Answer):

    def __init__(self):
        pass

    @classmethod
    def add(cls, num):
        return add(cls.answer, num)

    @classmethod
    def subtract(cls, num):
        return subtract(cls.answer, num)

    @classmethod
    def multiply(cls, num):
        return multiply(cls.answer, num)

    @classmethod
    def divide(cls, num):
        return divide(cls.answer, num)

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
