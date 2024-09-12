
class Animal:
    name = "I'm not named"
    weight = 100
    def __init__(self, weight):
        self.weight = weight

    def set_parent(self, animal):
        self.parent = animal

    def my_parent(self):
        if self.parent is not None:
            print("My parent is " + self.parent.name)

    def my_weight(self):
        print("My weight is " + str(self.weight))


class Dog(Animal):
    def __init__(self, name, weight):
        super().__init__(weight)
        self.name = name
    def speak(self):
        print(self.name + ": bark")

dog = Dog("Max", 50)
dog.speak()
dog2 = Dog("Fido",25)
dog2.set_parent(dog)
dog2.my_parent()
dog2.my_weight()
