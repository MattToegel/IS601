import MyCalc

calc = MyCalc.MyCalc()
calc.calc(2, "+", 2)
MyCalc.MyCalc.ans = 500

calc.calc("ans", "+", 1)
print("calc: " + str(calc.ans))
print("MyCalc: " + str(MyCalc.MyCalc.ans))
#calc2 = MyCalc()
