from datetime import datetime, date

import dates

def test_my_datetime():
    dt = datetime(2024, 1, 12, hour=3, minute=7, second=55)
    assert dates.my_datetime(dt) == "2024 01 12 03 07 55"

def test_saturdays():
    for d in dates.saturdays():
        assert d.weekday() == 5

def test_saturdays_stop():
    for d in dates.saturdays():
        assert d < date(date.today().year + 1, 1, 1)

def test_saturdays_in_order():
    prev_d = date(1970, 1, 1)
    for d in dates.saturdays():
        assert d > prev_d
        prev_d = d

def test_first_or_fifteenth():
    assert dates.first_or_fifteenth(date(2024, 1, 15)) == True
    assert dates.first_or_fifteenth(date(2024, 1, 12)) == False
    assert dates.first_or_fifteenth(date(2024, 6, 1)) == False
