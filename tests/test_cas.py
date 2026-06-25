import pytest

from calc.modes import cas


def _exact(op, expr, **kw):
    return cas.compute(op, expr, **kw)[0]


def test_diff():
    assert _exact("미분", "x**2") == "2*x"
    assert _exact("미분", "sin(x)") == "cos(x)"
    assert _exact("미분", "x**3", n="2") == "6*x"


def test_indefinite_integral():
    assert _exact("부정적분", "2*x") == "x**2"


def test_definite_integral():
    assert _exact("정적분", "sin(x)", a="0", b="pi") == "2"
    assert _exact("정적분", "x**2", a="0", b="1") == "1/3"


def test_limit():
    assert _exact("극한", "sin(x)/x", point="0") == "1"
    assert _exact("극한", "1/x", point="oo") == "0"


def test_factor_expand():
    assert _exact("인수분해", "x**2 - 1") == "(x - 1)*(x + 1)"
    assert _exact("전개", "(x+1)**2") == "x**2 + 2*x + 1"


def test_exact_keeps_surds_and_fractions():
    assert _exact("정확값", "sqrt(8)") == "2*sqrt(2)"
    assert _exact("정확값", "1/2 + 1/3") == "5/6"


def test_numeric_form():
    exact, approx = cas.compute("정확값", "sqrt(2)")
    assert exact == "sqrt(2)"
    assert approx.startswith("1.414")


def test_caret_is_power():
    assert _exact("정확값", "2^10") == "1024"


def test_parse_rejects_empty():
    with pytest.raises(ValueError):
        cas.parse("")


def test_parse_blocks_code_execution():
    # Names resolve to symbols / errors, never to builtins or attribute access.
    for bad in ["__import__('os')", "().__class__", "open('x')"]:
        with pytest.raises(ValueError):
            cas.parse(bad)
