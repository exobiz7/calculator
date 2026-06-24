"""Result formatting: decimal / fraction / scientific / thousands."""

from fractions import Fraction

MODES = ["자동", "천단위", "분수", "과학적"]


def _auto(value: float) -> str:
    if value != value or value in (float("inf"), float("-inf")):
        return "Error"
    if value == int(value) and abs(value) < 1e16:
        return str(int(value))
    return f"{value:.10g}"


def _thousands(value: float) -> str:
    if value != value or value in (float("inf"), float("-inf")):
        return "Error"
    if value == int(value) and abs(value) < 1e16:
        return f"{int(value):,}"
    return f"{value:,.6f}".rstrip("0").rstrip(".")


def _fraction(value: float) -> str:
    if value != value or value in (float("inf"), float("-inf")):
        return "Error"
    frac = Fraction(value).limit_denominator(1_000_000)
    if frac.denominator == 1:
        return str(frac.numerator)
    return f"{frac.numerator}/{frac.denominator}"


def _scientific(value: float) -> str:
    if value != value or value in (float("inf"), float("-inf")):
        return "Error"
    return f"{value:.6e}"


_FORMATTERS = {
    "자동": _auto,
    "천단위": _thousands,
    "분수": _fraction,
    "과학적": _scientific,
}


def format_value(value: float, mode: str = "자동") -> str:
    return _FORMATTERS.get(mode, _auto)(value)
