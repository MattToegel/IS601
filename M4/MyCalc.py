class MyCalc:
    ans = 0

    @staticmethod
    def _is_float(val):
        try:
            val = float(val)
            return True
        except:
            return False

    @staticmethod
    def _is_int(val):
        try:
            val = int(val)
            return True
        except:
            return False

    @staticmethod
    def _as_number(val):
        if MyCalc._is_int(val):
            return int(val)
        elif MyCalc._is_float(val):
            return float(val)
        else:
            raise Exception("Not a number")

    def calc(self, num1, num2, operator):
        if num1 == "ans":
            return self.calc(self.ans, num2, operator)
        num1 = MyCalc._as_number(num1)
        num2 = MyCalc._as_number(num2)

        if operator == "+":
            self.ans = num1+num2
        elif operator == "-":
            self.ans = num1-num2
        elif operator == "*":
            self.ans = num1*num2
        elif operator == "/":
            self.ans = num1/num2
        return self.ans

if __name__ == '__main__':
    is_running = True
    iSTR = input("Are you ready?")
    calc = MyCalc()
    print(calc)
    if iSTR == "yes":
        while is_running:
            iSTR = input("What is your eq:")
            if iSTR == "quit" or iSTR == "q":
                is_running = False
            else:
                print("Your eq was " + str(iSTR))
                ops = ["+", "/", "*","-"]
                for op in ops:
                    if op in iSTR:
                        nums = iSTR.split(op)
                        r = calc.calc(nums[0].strip(), nums[1].strip(), op)
                        print("R is " + str(r))





    else:
        print("Good bye")
        is_running = False
