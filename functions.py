def my_func(num1, num2):
    print(num1)
    print(num2)
    return num1 * num2


class MyClass:
    __secreteValue = "test"
    __money = 0;
    def __init__(self, name, money):
        self.name = name
        self.__money = money
        print("Hello I'm " + self.name)
        print("Secret: " + self.__secreteValue)

    def give_money(self, val):
        self.__money += val

    def show_money(self):
        print(self.__money)

#print(my_func(2, 2))
john = MyClass("John",50)
bob = MyClass("Bob",25)
bob.give_money(5)
bob.show_money()
john.give_money(bob.__money)
