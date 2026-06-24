"""Numerical analysis on expressions in x: derivative, integral, root finding.

All evaluate the expression via the shared safe_eval with variables={"x": ...},
so any function/constant the scientific mode supports works here too. No symbolic
math (that is the future CAS phase) and no extra dependencies.
"""

from collections.abc import Callable

from calc.core.expr import safe_eval


def make_f(expr: str, angle: str = "RAD") -> Callable[[float], float]:
    """Return f(x) = expr evaluated with x bound to the argument."""

    def f(x: float) -> float:
        return float(safe_eval(expr, angle, variables={"x": x}))

    return f


def nderiv(expr: str, x0: float, angle: str = "RAD", h: float = 1e-5) -> float:
    """Numerical derivative f'(x0) via the central difference."""
    f = make_f(expr, angle)
    return (f(x0 + h) - f(x0 - h)) / (2 * h)


def integrate(
    expr: str, a: float, b: float, angle: str = "RAD", n: int = 1000
) -> float:
    """Definite integral ∫_a^b f(x) dx via Simpson's rule."""
    if a == b:
        return 0.0
    n = max(2, n)
    if n % 2:
        n += 1  # Simpson needs an even number of intervals
    f = make_f(expr, angle)
    h = (b - a) / n
    total = f(a) + f(b)
    for i in range(1, n):
        total += (4 if i % 2 else 2) * f(a + i * h)
    return total * h / 3


def solve(
    expr: str,
    angle: str = "RAD",
    guess: float = 1.0,
    tol: float = 1e-10,
    max_iter: int = 100,
) -> float:
    """Find a root of f(x) = 0 (expr) — Newton's method, bisection fallback.

    The expression is the left side of "f(x) = 0"; an "= 0" suffix is tolerated.
    """
    expr = expr.strip()
    if expr.endswith("= 0"):
        expr = expr[:-3]
    elif expr.endswith("=0"):
        expr = expr[:-2]
    f = make_f(expr, angle)

    # Newton's method from the initial guess.
    x = guess
    for _ in range(max_iter):
        try:
            fx = f(x)
        except (ValueError, ZeroDivisionError, OverflowError):
            break
        if abs(fx) < tol:
            return x
        d = (f(x + 1e-7) - f(x - 1e-7)) / (2e-7)
        if d == 0:
            break
        step = fx / d
        x -= step
        if abs(step) < tol:
            return x

    # Bisection fallback: scan a wide range for a sign change, then bisect.
    lo, hi, steps = -1000.0, 1000.0, 4000
    prev_x = lo
    try:
        prev = f(lo)
    except (ValueError, ZeroDivisionError, OverflowError):
        prev = None
    for i in range(1, steps + 1):
        cur_x = lo + (hi - lo) * i / steps
        try:
            cur = f(cur_x)
        except (ValueError, ZeroDivisionError, OverflowError):
            prev_x, prev = cur_x, None
            continue
        if prev is not None and prev == prev and cur == cur and prev * cur <= 0:
            a, fa = prev_x, prev
            b = cur_x
            for _ in range(200):
                m = (a + b) / 2
                fm = f(m)
                if abs(fm) < tol:
                    return m
                if fa * fm < 0:
                    b = m
                else:
                    a, fa = m, fm
            return (a + b) / 2
        prev_x, prev = cur_x, cur

    raise ValueError("근을 찾지 못했습니다 (초기값을 바꿔보세요)")
