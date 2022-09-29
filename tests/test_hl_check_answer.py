from HigherLower_005_v3 import HigherLower
import pytest

@pytest.fixture
def game():
    hl =  HigherLower()
    hl.latest_number = 5
    
    return hl

def test_check_answer_higher_pos(game):
    assert game._check_answer("higher", 10)

def test_check_answer_lower_pos(game):

    assert game._check_answer("lower", 1)

def test_check_answer_higher_neg(game):
    assert not game._check_answer("higher", 1)

def test_check_answer_lower_neg(game):

    assert not game._check_answer("lower", 10)