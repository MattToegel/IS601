from MyCalc import MyCalc


def test_add():
    calc = MyCalc()
    check = calc.calc(2, 2, "+")
    assert check == 4
