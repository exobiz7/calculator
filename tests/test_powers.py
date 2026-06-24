import math

import pytest

from calc.core import powers


def test_square_and_power():
    assert powers.square(5) == 25
    assert powers.power(2, 10) == 1024
    assert powers.power(2, 0.5) == pytest.approx(math.sqrt(2))


def test_sqrt():
    assert powers.sqrt(9) == 3
    with pytest.raises(ValueError):
        powers.sqrt(-1)


def test_nth_root():
    assert powers.nth_root(27, 3) == pytest.approx(3)
    assert powers.nth_root(-8, 3) == pytest.approx(-2)  # odd root of negative
    with pytest.raises(ValueError):
        powers.nth_root(-4, 2)  # even root of negative
    with pytest.raises(ValueError):
        powers.nth_root(4, 0)


def test_reciprocal():
    assert powers.reciprocal(4) == 0.25
    with pytest.raises(ValueError):
        powers.reciprocal(0)
