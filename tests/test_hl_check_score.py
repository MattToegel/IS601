from HigherLower_005_v3 import HigherLower
import pytest

@pytest.fixture
def game():
    hl =  HigherLower()
    hl.score = 0
    return hl

def test_is_correct_pos(game):
    game._check_score(True)
    assert game.score == game.score_increment

def test_is_not_correct_pos(game):
    game._check_score(False)
    assert game.score == 0

def test_is_not_correct_neg(game):
    game._check_score(False)
    assert not game.score == game.score_increment

def test_is_correct_neg(game):
    game._check_score(True)
    assert not game.score == 0