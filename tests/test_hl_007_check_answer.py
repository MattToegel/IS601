import pytest;
from HigherLower_007_v3 import HigherLower

@pytest.fixture
def hl():
    hl = HigherLower()
    return hl

def test_check_guess_higher(hl):
    hl.guess = "higher"
    assert hl.check_guess()