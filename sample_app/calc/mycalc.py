import operator  # https://docs.python.org/3/library/operator.html

# TODO idea
# 1) Allow longer equations
# 2) expand math functions
# 3) Separate calculator answers
# 4) Support config options (i.e., rounding logic, answer conversion)
# 5) Persist last answer between application restarts
# 6) Record eq history


class MyCalc:
    ans = 0  # todo, class vs static vs instance
    ops = {'+': operator.add,
           '-': operator.sub,
           '*': operator.mul,
           'x': operator.mul,
           '/': operator.truediv}


    @staticmethod
    def _is_float(val):
        try:
            float(val)
            return True
        except:
            return False

    @staticmethod
    def _is_int(val):
        try:
            int(val)
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

    def calc(self, num1, op, num2):
        # map characters to operator function references
        # https://stackoverflow.com/a/18591880
        # print("num1: " + str(num1))
        # print("num2: " + str(num2))
        if num1 == "ans":
            return self.calc(self.ans, op, num2)
        else:
            num1 = self._as_number(num1)
            num2 = self._as_number(num2)
            self.ans = MyCalc.ops[op](num1, num2)
        return self.ans

class AdvMyCalc(MyCalc):
    def __init__(self):
        super().ops["**"] = operator.pow
        super().ops["//"] = operator.floordiv
        super().ops["%"] = operator.mod


if __name__ == '__main__':
    is_running = True
    iSTR = input("Are you ready?")
    #calc = MyCalc()
    calc = AdvMyCalc()
    print(calc)
    if iSTR == "yes":
        while is_running:
            iSTR = input("What is your eq:")
            if iSTR == "quit" or iSTR == "q":
                is_running = False
            else:
                print("Your eq was " + str(iSTR))
                checks = ["+", "**", "//",  "/", "*", "x", "-", "%"]
                handled = False
                for check in checks:
                    if not handled and check in iSTR:
                        nums = iSTR.split(check)
                        r = calc.calc(nums[0].strip(), check, nums[1].strip())
                        print("R is " + str(r))
                        handled = True
                if not handled:
                    print("The action you tried is not supported, please try again")
    else:  # exit loop
        print("Good bye")
        is_running = False
