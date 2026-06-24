"""Scientific calculator engine: textbook-style expression entry.

Unlike the immediate-execution basic engine, the scientific mode builds a full
expression string (with parentheses and functions) and evaluates it at once via
:mod:`calc.core.expr`. Angle mode (DEG/RAD) is carried here.
"""

from calc.core import ratio
from calc.core.expr import safe_eval
from calc.modes.basic import format_number

VALID_ANGLES = ("RAD", "DEG")


class ScientificEngine:
    def __init__(self) -> None:
        self.expression = ""
        self.result = "0"
        self.angle = "RAD"
        self.last_answer = 0.0
        self.error = False

    # --- expression editing --------------------------------------------
    def insert(self, token: str) -> None:
        if self.error:
            self.clear()
        self.expression += token

    def backspace(self) -> None:
        self.expression = self.expression[:-1]

    def clear(self) -> None:
        self.expression = ""
        self.result = "0"
        self.error = False

    def set_angle(self, angle: str) -> None:
        if angle.upper() in VALID_ANGLES:
            self.angle = angle.upper()

    def toggle_angle(self) -> str:
        self.angle = "DEG" if self.angle == "RAD" else "RAD"
        return self.angle

    # --- evaluation -----------------------------------------------------
    def evaluate(self) -> str:
        try:
            value = safe_eval(self.expression, self.angle)
            self.result = format_number(float(value))
            self.last_answer = float(value)
            self.error = self.result == "Error"
        except (ValueError, ZeroDivisionError, OverflowError):
            self.result = "Error"
            self.error = True
        return self.result

    def use_answer(self) -> None:
        """Insert the previous answer into the expression."""
        self.insert(format_number(self.last_answer))

    # --- bonus: proportion helper --------------------------------------
    @staticmethod
    def solve_proportion(a: float, b: float, x: float) -> float:
        """a : b = x : ?  ->  y"""
        return ratio.solve_simple(a, b, x)

    @staticmethod
    def solve_triple(a: float, b: float, c: float, x: float) -> tuple[float, float]:
        """a : b : c = x : ? : ?  ->  (y, z)"""
        return ratio.solve_triple(a, b, c, x)
