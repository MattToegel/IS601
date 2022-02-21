from MyCalc import MyCalc


def test_add():
    calc = MyCalc()
    check = calc.add(2, 2)
    assert check == 4
