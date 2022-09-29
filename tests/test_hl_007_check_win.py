import pytest;
from HigherLower_007_v3 import HigherLower

@pytest.fixture
def hl():
    hl = HigherLower()
    return hl

def test_win_higher_add_point_pos(hl):
    hl.guess = "higher"
    hl.number = 5
    hl.score = 0
    hl.check_win(10) # param is new_number
    assert hl.score == hl.score_increment

def test_win_higher_add_point_neg(hl):
    hl.guess = "higher"
    hl.number = 5
    hl.score = 0
    hl.check_win(10) # param is new_number
    assert not hl.score == 0

def test_win_lower_add_point_pos(hl):
    hl.guess = "lower"
    hl.number = 5
    hl.score = 0
    hl.check_win(1) # param is new_number
    assert hl.score == hl.score_increment