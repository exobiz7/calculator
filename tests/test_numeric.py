import math

import pytest

from calc.core.numeric import integrate, nderiv, solve


def test_nderiv():
    assert nderiv("x**2", 3) == pytest.approx(6, abs=1e-4)  # d/dx x² = 2x
    assert nderiv("x**3", 2) == pytest.approx(12, abs=1e-3)  # 3x²
    assert nderiv("sin(x)", 0) == pytest.approx(1, abs=1e-6)  # cos(0)=1


def test_integrate():
    assert integrate("x**2", 0, 1) == pytest.approx(1 / 3, abs=1e-6)
    assert integrate("x", 0, 10) == pytest.approx(50, abs=1e-9)
    assert integrate("sin(x)", 0, math.pi) == pytest.approx(2, abs=1e-6)


def test_integrate_zero_width():
    assert integrate("x**2", 5, 5) == 0.0


def test_solve_newton():
    assert solve("x**2 - 2", guess=1.0) == pytest.approx(math.sqrt(2), abs=1e-6)
    assert solve("x - 5") == pytest.approx(5, abs=1e-9)


def test_solve_tolerates_equals_zero_suffix():
    assert solve("x**2 - 2 = 0", guess=1.0) == pytest.approx(math.sqrt(2), abs=1e-6)


def test_solve_bisection_fallback():
    # cos(x) = 0 near pi/2; poor guess forces the scan/bisection path
    root = solve("cos(x)", guess=1000.0)
    assert math.cos(root) == pytest.approx(0, abs=1e-6)


def test_solve_no_root_raises():
    with pytest.raises(ValueError):
        solve("x**2 + 1", guess=0.0)  # no real root
