import pytest

from calc.core.arithmetic import calculate, divide


def test_basic_operations():
    assert calculate(2, "+", 3) == 5
    assert calculate(10, "-", 4) == 6
    assert calculate(6, "*", 7) == 42
    assert calculate(20, "/", 5) == 4


def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(1, 0)


def test_unknown_operator():
    with pytest.raises(ValueError):
        calculate(1, "^", 2)
