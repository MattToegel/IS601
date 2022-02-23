import csv

import pytest

from M4.MyCalc import MyCalc


# Options for Pos/Neg
# Options 1: Have logic in testcase to handle both scenarios
# Not ideal due to difficulty in labeling assertion output

# Option 2: Have two separate cases (positive/negative)
# "Half" of the cases will fail in each, but the SUM of the tests should all pass accordingly

# For MP2 use this option (but feel free to explore others)
# Option 3: Split data into positive test case data and negative test case data
# Pass respective chunks of data to respective positive/negative test case



def grab_test_file2():
    with open("random2.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        rows = []
        for row in csv_reader:
            if line_count > 0:
                rows.append(row)
            line_count += 1
        return rows

# Option 1 https://stackoverflow.com/questions/45879028/pytest-parameterized-test-with-custom-id-function
@pytest.mark.parametrize(argnames=("name","v1","v2", "ea"),argvalues=grab_test_file2(), ids=[i[0] for i in grab_test_file2()])
def test_csvmult(name, v1,v2, ea):
    calc = MyCalc()
    r = calc.calc(v1, v2, "*")
    if name == "positive":
        assert r == int(ea)
    else:
        assert r != int(ea)


def grab_test_file():
    with open("random.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        rows = []
        for row in csv_reader:
            if line_count > 0:
                rows.append(row)
            line_count += 1
        return rows
# Option 2
@pytest.mark.parametrize("row", grab_test_file())
def test_csvmult_pos(row):
    calc = MyCalc()
    r = calc.calc(row[0], row[1], "*")
    assert r == int(row[2])

@pytest.mark.parametrize("row", grab_test_file())
def test_csvmult_neg(row):
    calc = MyCalc()
    r = calc.calc(row[0], row[1], "*")
    assert r != int(row[2])
