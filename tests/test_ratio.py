import pytest

from calc.core import ratio


def test_solve_simple():
    assert ratio.solve_simple(2, 3, 4) == pytest.approx(6)
    assert ratio.solve_simple(5, 10, 7) == pytest.approx(14)


def test_solve_simple_zero_a():
    with pytest.raises(ValueError):
        ratio.solve_simple(0, 3, 4)


def test_solve_triple():
    assert ratio.solve_triple(1, 2, 3, 5) == pytest.approx((10, 15))
    assert ratio.solve_triple(2, 4, 6, 1) == pytest.approx((2, 3))


def test_solve_triple_zero_a():
    with pytest.raises(ValueError):
        ratio.solve_triple(0, 2, 3, 5)
