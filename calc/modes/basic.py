"""Basic calculator engine (immediate-execution, like a desktop calculator).

The engine is UI-agnostic and fully testable: feed it button events and read
``display``. The Tkinter view in ``calc/ui`` is a thin wrapper over this.
"""

from calc.core import powers
from calc.core.arithmetic import calculate
from calc.core.memory import GrandTotal, Memory

_BINARY_OPS = {"+", "-", "*", "/"}


def format_number(value: float) -> str:
    """Render a float the way a calculator would (no trailing .0 for ints)."""
    if value != value or value in (float("inf"), float("-inf")):
        return "Error"
    if value == int(value) and abs(value) < 1e16:
        return str(int(value))
    # Trim floating noise while keeping precision reasonable.
    return f"{value:.10g}"


class CalculatorEngine:
    """Immediate-execution calculator with memory and grand-total registers."""

    def __init__(self) -> None:
        self.memory = Memory()
        self.grand_total = GrandTotal()
        self.all_clear()

    # --- state ----------------------------------------------------------
    def all_clear(self) -> None:
        """AC: clear entry and pending operation (memory/GT persist)."""
        self.display = "0"
        self._accumulator: float | None = None
        self._pending_op: str | None = None
        self._reset_on_next_digit = True
        self.error = False

    def clear_entry(self) -> None:
        """C: clear only the current entry."""
        if self.error:
            self.all_clear()
            return
        self.display = "0"
        self._reset_on_next_digit = True

    @property
    def current(self) -> float:
        try:
            return float(self.display)
        except ValueError:
            return 0.0

    def _show(self, value: float) -> None:
        self.display = format_number(value)
        self.error = self.display == "Error"

    # --- entry ----------------------------------------------------------
    def input_digit(self, digit: str) -> None:
        if self.error:
            self.all_clear()
        if self._reset_on_next_digit or self.display == "0":
            self.display = digit
            self._reset_on_next_digit = False
        else:
            self.display += digit

    def input_dot(self) -> None:
        if self.error:
            self.all_clear()
        if self._reset_on_next_digit:
            self.display = "0."
            self._reset_on_next_digit = False
        elif "." not in self.display:
            self.display += "."

    def backspace(self) -> None:
        if self.error or self._reset_on_next_digit:
            return
        self.display = self.display[:-1] or "0"
        if self.display in ("", "-"):
            self.display = "0"

    # --- operations -----------------------------------------------------
    def set_operator(self, op: str) -> None:
        if op not in _BINARY_OPS or self.error:
            return
        if self._pending_op is not None and not self._reset_on_next_digit:
            self._compute()
        else:
            self._accumulator = self.current
        self._pending_op = op
        self._reset_on_next_digit = True

    def equals(self) -> None:
        if self._pending_op is None or self.error:
            return
        self._compute()
        self.grand_total.accumulate(self.current)
        self._pending_op = None
        self._reset_on_next_digit = True

    def _compute(self) -> None:
        if self._pending_op is None or self._accumulator is None:
            return
        try:
            result = calculate(self._accumulator, self._pending_op, self.current)
        except ValueError:
            self.display = "Error"
            self.error = True
            self._accumulator = None
            self._pending_op = None
            return
        self._show(result)
        self._accumulator = result

    # --- unary ----------------------------------------------------------
    def negate(self) -> None:
        if self.error or self.display in ("0", "0."):
            return
        if self.display.startswith("-"):
            self.display = self.display[1:]
        else:
            self.display = "-" + self.display

    def percent(self) -> None:
        """Context-aware %, matching common desktop calculators."""
        if self.error:
            return
        value = self.current
        if self._pending_op in ("+", "-") and self._accumulator is not None:
            self._show(self._accumulator * value / 100)
        elif self._pending_op in ("*", "/"):
            self._show(value / 100)
        else:
            self._show(value / 100)
        self._reset_on_next_digit = True

    def _apply_unary(self, fn) -> None:
        if self.error:
            return
        try:
            self._show(fn(self.current))
        except ValueError:
            self.display = "Error"
            self.error = True
        self._reset_on_next_digit = True

    def square(self) -> None:
        self._apply_unary(powers.square)

    def square_root(self) -> None:
        self._apply_unary(powers.sqrt)

    def reciprocal(self) -> None:
        self._apply_unary(powers.reciprocal)

    # --- memory ---------------------------------------------------------
    def memory_add(self) -> None:
        if not self.error:
            self.memory.add(self.current)
            self._reset_on_next_digit = True

    def memory_subtract(self) -> None:
        if not self.error:
            self.memory.subtract(self.current)
            self._reset_on_next_digit = True

    def memory_recall(self) -> None:
        if not self.error:
            self._show(self.memory.recall())
            self._reset_on_next_digit = True

    def memory_clear(self) -> None:
        self.memory.clear()
