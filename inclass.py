
class Wrapper:
    x = 5
    def recur(self, num):
        num -= 1
        print(num)
        if True:
            print("recur " + str(num))
            self.recur(num)


obj1 = Wrapper()
obj1.recur(3)
