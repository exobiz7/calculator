import math

import pytest

from calc.core.expr import safe_eval


def test_variables():
    assert safe_eval("a / b * 100", variables={"a": 100, "b": 500}) == pytest.approx(20)
    assert safe_eval("price - cost", variables={"price": 5000, "cost": 3000}) == 2000
    # unknown variable still rejected
    with pytest.raises(ValueError):
        safe_eval("a + missing", variables={"a": 1})
    # no variables passed -> names rejected as before (backward compatible)
    with pytest.raises(ValueError):
        safe_eval("a + 1")


def test_arithmetic_and_precedence():
    assert safe_eval("2 + 3 * 4") == 14
    assert safe_eval("(2 + 3) * 4") == 20
    assert safe_eval("2 ** 10") == 1024
    assert safe_eval("7 % 3") == 1


def test_constants_and_functions():
    assert safe_eval("pi") == pytest.approx(math.pi)
    assert safe_eval("sqrt(2)") == pytest.approx(math.sqrt(2))
    assert safe_eval("ln(e)") == pytest.approx(1)
    assert safe_eval("log(1000)") == pytest.approx(3)
    assert safe_eval("fact(5)") == 120


def test_angle_modes():
    assert safe_eval("sin(30)", angle="DEG") == pytest.approx(0.5)
    assert safe_eval("sin(pi/2)", angle="RAD") == pytest.approx(1.0)
    assert safe_eval("asin(1)", angle="DEG") == pytest.approx(90)


def test_unicode_normalization():
    assert safe_eval("2 × 3") == 6
    assert safe_eval("10 ÷ 4") == pytest.approx(2.5)
    assert safe_eval("2 ^ 3") == 8


def test_rejects_unsafe_input():
    for bad in ["__import__('os')", "open('x')", "x + 1", "1; 2", "lambda: 1"]:
        with pytest.raises(ValueError):
            safe_eval(bad)
