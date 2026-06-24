"""Scientific calculator engine: textbook-style expression entry.

Unlike the immediate-execution basic engine, the scientific mode builds a full
expression string (with parentheses and functions) and evaluates it at once via
:mod:`calc.core.expr`. Angle mode (DEG/RAD), the previous answer (Ans), and user
variables (e.g. ``A = 3+4``) are carried here.
"""

import re

from calc.core.expr import _CONSTANTS, safe_eval
from calc.modes.basic import format_number

VALID_ANGLES = ("RAD", "DEG")
_ASSIGN = re.compile(r"^\s*([A-Za-z]\w*)\s*=\s*(.+)$")


class ScientificEngine:
    def __init__(self) -> None:
        self.expression = ""
        self.result = "0"
        self.angle = "RAD"
        self.last_answer = 0.0
        self.error = False
        self.variables: dict[str, float] = {}

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
    def _scope(self) -> dict:
        return {**self.variables, "Ans": self.last_answer, "ans": self.last_answer}

    def evaluate(self) -> str:
        text = self.expression.strip()
        assign = _ASSIGN.match(text)
        # Treat as assignment only for "name = rhs" (not "==" comparisons).
        if assign and not text.lstrip().startswith("=") and "==" not in text:
            name, rhs = assign.group(1), assign.group(2)
            if name in _CONSTANTS:
                self.result, self.error = "Error", True
                return self.result
            expr = rhs
        else:
            name, expr = None, text
        try:
            value = float(safe_eval(expr, self.angle, variables=self._scope()))
            self.last_answer = value
            if name is not None:
                self.variables[name] = value
            self.result = format_number(value)
            self.error = self.result == "Error"
        except (ValueError, ZeroDivisionError, OverflowError):
            self.result = "Error"
            self.error = True
        return self.result

    def use_answer(self) -> None:
        """Insert the previous answer into the expression."""
        self.insert(format_number(self.last_answer))
