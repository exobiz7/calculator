"""Memory and grand-total registers, modeled on commercial calculators.

- M+ / M- / MR / MC  : the classic memory register.
- GT (grand total)   : accumulates each completed result, like Casio business
  calculators. Press GT to read the running total, GT-clear to reset.
"""


class Memory:
    """A single accumulating memory register (M+/M-/MR/MC)."""

    def __init__(self) -> None:
        self._value: float = 0.0

    @property
    def value(self) -> float:
        return self._value

    @property
    def has_value(self) -> bool:
        return self._value != 0.0

    def add(self, x: float) -> float:
        """M+ : add x to memory."""
        self._value += x
        return self._value

    def subtract(self, x: float) -> float:
        """M- : subtract x from memory."""
        self._value -= x
        return self._value

    def recall(self) -> float:
        """MR : read the stored value."""
        return self._value

    def clear(self) -> None:
        """MC : reset memory to zero."""
        self._value = 0.0


class GrandTotal:
    """GT register: sums every result fed to it via accumulate()."""

    def __init__(self) -> None:
        self._total: float = 0.0

    @property
    def total(self) -> float:
        return self._total

    def accumulate(self, result: float) -> float:
        """Add a completed calculation result to the grand total."""
        self._total += result
        return self._total

    def clear(self) -> None:
        self._total = 0.0
