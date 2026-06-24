"""Power / root functions shared across calculator modes."""

import math


def square(x: float) -> float:
    """Return x squared (x ** 2)."""
    return x**2


def power(x: float, n: float) -> float:
    """Return x raised to the n-th power (x ** n)."""
    return x**n


def sqrt(x: float) -> float:
    """Return the square root of x."""
    if x < 0:
        raise ValueError("Cannot take the square root of a negative number")
    return math.sqrt(x)


def nth_root(x: float, n: float) -> float:
    """Return the n-th root of x (x ** (1/n))."""
    if n == 0:
        raise ValueError("Root degree 'n' cannot be zero")
    if x < 0 and int(n) == n and int(n) % 2 == 1:
        # Real odd root of a negative number.
        return -((-x) ** (1.0 / n))
    if x < 0:
        raise ValueError("Cannot take an even root of a negative number")
    return x ** (1.0 / n)


def reciprocal(x: float) -> float:
    """Return 1 / x."""
    if x == 0:
        raise ValueError("Cannot divide by zero")
    return 1.0 / x
