import math

import pytest

from calc.core.plotting import sample


def test_sample_length_and_endpoints():
    xs, ys = sample("x**2", -2, 2, n=4)
    assert len(xs) == 5 and len(ys) == 5
    assert xs[0] == -2 and xs[-1] == 2
    assert ys[0] == pytest.approx(4) and ys[2] == pytest.approx(0)


def test_sample_invalid_points_become_nan():
    xs, ys = sample("1/x", -1, 1, n=2)  # x=0 at the midpoint
    assert math.isnan(ys[1])
    assert math.isfinite(ys[0]) and math.isfinite(ys[2])


def test_sample_bad_range_raises():
    with pytest.raises(ValueError):
        sample("x", 1, 1)
