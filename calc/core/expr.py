"""Safe mathematical expression evaluator (no ``eval``).

Parses an expression with ``ast`` and walks a whitelist of node types, so only
arithmetic, a fixed set of math functions, and known constants are allowed.
Trigonometric functions honor the angle mode ("DEG" or "RAD").
"""

import ast
import math
import operator

_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}
_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_CONSTANTS = {"pi": math.pi, "e": math.e, "tau": math.tau}

# Unicode operators users might type, normalized to Python syntax.
_NORMALIZE = {"×": "*", "÷": "/", "−": "-", "^": "**", "π": "pi", "√": "sqrt"}


def _factorial(x: float) -> int:
    if x < 0 or x != int(x):
        raise ValueError("factorial requires a non-negative integer")
    return math.factorial(int(x))


def _build_functions(angle: str) -> dict:
    deg = angle.upper() == "DEG"

    def t(fn):  # forward trig: convert input degrees -> radians
        return (lambda x: fn(math.radians(x))) if deg else fn

    def it(fn):  # inverse trig: convert radian result -> degrees
        return (lambda x: math.degrees(fn(x))) if deg else fn

    return {
        "sin": t(math.sin),
        "cos": t(math.cos),
        "tan": t(math.tan),
        "asin": it(math.asin),
        "acos": it(math.acos),
        "atan": it(math.atan),
        "sqrt": math.sqrt,
        "cbrt": lambda x: math.copysign(abs(x) ** (1 / 3), x),
        "ln": math.log,
        "log": math.log10,
        "log2": math.log2,
        "exp": math.exp,
        "abs": abs,
        "fact": _factorial,
        "floor": math.floor,
        "ceil": math.ceil,
        "round": round,
    }


def safe_eval(
    expression: str, angle: str = "RAD", variables: dict | None = None
) -> float:
    """Evaluate a math expression. Raises ValueError on anything unsupported.

    ``variables`` maps names to numbers, resolved after the built-in constants.
    This is the shared, sandboxed evaluator for the scientific, KPI, and (future)
    AI-formula modes — model-proposed formulas are run here, never via ``exec``.
    """
    text = expression.strip()
    if not text:
        raise ValueError("empty expression")
    variables = variables or {}
    for bad, good in _NORMALIZE.items():
        text = text.replace(bad, good)

    funcs = _build_functions(angle)

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
                raise ValueError("only numbers are allowed")
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _BINOPS:
            return _BINOPS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY:
            return _UNARY[type(node.op)](_eval(node.operand))
        if isinstance(node, ast.Name):
            if node.id in _CONSTANTS:
                return _CONSTANTS[node.id]
            if node.id in variables:
                return variables[node.id]
            raise ValueError(f"unknown name: {node.id}")
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in funcs:
                raise ValueError("unknown function")
            args = [_eval(a) for a in node.args]
            return funcs[node.func.id](*args)
        raise ValueError("unsupported expression")

    try:
        tree = ast.parse(text, mode="eval")
    except SyntaxError as exc:
        raise ValueError("invalid expression") from exc
    try:
        return _eval(tree)
    except (ZeroDivisionError, OverflowError) as exc:
        raise ValueError(str(exc) or "math error") from exc
