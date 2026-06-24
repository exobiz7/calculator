"""Sampling for the graphing mode (matplotlib-free, testable).

Evaluates y = f(x) over a range via the shared safe_eval (reusing numeric.make_f).
Invalid points (domain errors, division by zero, non-finite) become NaN so the
plot shows a gap rather than failing.
"""

import math

from calc.core.numeric import make_f


def sample(
    expr: str, xmin: float, xmax: float, angle: str = "RAD", n: int = 400
) -> tuple[list[float], list[float]]:
    """Return (xs, ys) sampling expr over [xmin, xmax]; invalid y -> NaN."""
    if xmax <= xmin:
        raise ValueError("xmax는 xmin보다 커야 합니다")
    n = max(2, n)
    f = make_f(expr, angle)
    xs: list[float] = []
    ys: list[float] = []
    for i in range(n + 1):
        x = xmin + (xmax - xmin) * i / n
        xs.append(x)
        try:
            y = f(x)
            ys.append(y if math.isfinite(y) else float("nan"))
        except (ValueError, ZeroDivisionError, OverflowError):
            ys.append(float("nan"))
    return xs, ys
