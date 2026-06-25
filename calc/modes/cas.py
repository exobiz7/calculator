"""Symbolic math (CAS) via sympy.

Separate from the float-only safe_eval: this path keeps exact forms (fractions,
surds, pi). Parsing uses sympy's parse_expr with a function whitelist plus a
character/attribute guard (never eval/sympify on raw strings), so input cannot
execute arbitrary code — unknown names simply become symbols.
"""

import re

from sympy import (
    Abs,
    E,
    acos,
    asin,
    atan,
    cos,
    cosh,
    diff,
    exp,
    expand,
    factor,
    factorial,
    integrate,
    limit,
    log,
    oo,
    pi,
    simplify,
    sin,
    sinh,
    sqrt,
    tan,
    tanh,
)
from sympy import Symbol
from sympy.parsing.sympy_parser import (
    convert_xor,
    parse_expr,
    standard_transformations,
)

OPS = ["간소화", "전개", "인수분해", "미분", "부정적분", "정적분", "극한", "정확값"]

_LOCAL = {
    "sin": sin,
    "cos": cos,
    "tan": tan,
    "asin": asin,
    "acos": acos,
    "atan": atan,
    "sinh": sinh,
    "cosh": cosh,
    "tanh": tanh,
    "exp": exp,
    "log": log,
    "ln": log,
    "sqrt": sqrt,
    "factorial": factorial,
    "abs": Abs,
    "Abs": Abs,
    "pi": pi,
    "e": E,
    "E": E,
    "oo": oo,
    "inf": oo,
    "infinity": oo,
}
_TRANS = standard_transformations + (convert_xor,)

# Only math-y characters; block dunders and attribute access (e.g. ().__class__,
# x.attr) so parse_expr can't be steered toward Python internals. A "." is only
# allowed as a decimal point (digit or operator on its left), never after a
# name/closing bracket.
_ALLOWED = re.compile(r"^[0-9A-Za-z_+\-*/^().,\s]+$")
_ATTR_ACCESS = re.compile(r"[A-Za-z_)\]]\s*\.")


def parse(expr_str: str):
    """Safely parse a math expression into a sympy object."""
    if not expr_str or not expr_str.strip():
        raise ValueError("식이 비어 있습니다")
    text = expr_str.strip()
    if len(text) > 500:
        raise ValueError("식이 너무 깁니다")
    if "__" in text or _ATTR_ACCESS.search(text) or not _ALLOWED.match(text):
        raise ValueError("허용되지 않는 입력입니다")
    try:
        return parse_expr(text, local_dict=_LOCAL, transformations=_TRANS)
    except (SyntaxError, TypeError, ValueError, AttributeError) as exc:
        raise ValueError(f"식을 해석할 수 없습니다: {exc}") from exc


def _format(expr) -> tuple[str, str]:
    """Return (exact_str, numeric_str). Numeric falls back to exact if N/A."""
    exact = str(expr)
    try:
        approx = str(expr.evalf(10))
    except (AttributeError, TypeError, ValueError):
        approx = exact
    return exact, approx


def compute(
    op: str,
    expr: str,
    var: str = "x",
    n: str = "1",
    a: str = "0",
    b: str = "1",
    point: str = "0",
) -> tuple[str, str]:
    """Dispatch a CAS operation; returns (exact, numeric) strings."""
    e = parse(expr)
    x = Symbol(var or "x")
    if op == "간소화":
        return _format(simplify(e))
    if op == "전개":
        return _format(expand(e))
    if op == "인수분해":
        return _format(factor(e))
    if op == "미분":
        return _format(diff(e, x, int(float(n))))
    if op == "부정적분":
        return _format(integrate(e, x))
    if op == "정적분":
        return _format(integrate(e, (x, parse(a), parse(b))))
    if op == "극한":
        return _format(limit(e, x, parse(point)))
    if op == "정확값":
        return _format(e)
    raise ValueError(f"알 수 없는 연산: {op}")
