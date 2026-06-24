"""Proportion (ratio) calculator module."""


def solve_simple(a: float, b: float, x: float) -> float:
    """Solve y for the proportion a : b = x : y.

    y = b * x / a
    """
    if a == 0:
        raise ValueError("First term 'a' cannot be zero")
    return b * x / a


def solve_triple(a: float, b: float, c: float, x: float) -> tuple[float, float]:
    """Solve (y, z) for the proportion a : b : c = x : y : z.

    Scales the ratio by x / a, then returns (y, z).
    """
    if a == 0:
        raise ValueError("First term 'a' cannot be zero")
    scale = x / a
    return b * scale, c * scale
