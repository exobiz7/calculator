"""Tkinter view for the basic calculator mode."""

import tkinter as tk

import ttkbootstrap as ttk

from calc.modes.basic import CalculatorEngine, format_number

_KEY_TO_DIGIT = set("0123456789")

# bootstyle conventions shared across modes
NUM = "light"  # digits
OP = "primary"  # operators (clay)
EQ = "success"  # equals (green)
MEM = "secondary"  # memory
UTIL = "secondary-outline"  # clear / backspace
FUNC = "info-outline"  # unary functions


class BasicView(ttk.Frame):
    """Button grid + display wired to a CalculatorEngine."""

    def __init__(self, master: tk.Misc, on_record=None) -> None:
        super().__init__(master, padding=10)
        self.engine = CalculatorEngine()
        self._on_record = on_record
        self._display_var = tk.StringVar(value="0")
        self._status_var = tk.StringVar(value="")
        self._build()
        self._refresh()

    def _equals_and_record(self) -> None:
        e = self.engine
        a, op, b = e._accumulator, e._pending_op, e.current
        e.equals()
        if self._on_record and op is not None and not e.error:
            expr = f"{format_number(a)} {op} {format_number(b)}"
            self._on_record(expr, e.display)

    def _build(self) -> None:
        ttk.Label(
            self, textvariable=self._status_var, anchor="w", bootstyle="secondary"
        ).grid(row=0, column=0, columnspan=4, sticky="we")

        ttk.Label(
            self,
            textvariable=self._display_var,
            anchor="e",
            font=("Helvetica", 32, "bold"),
            bootstyle="inverse-light",
            padding=12,
        ).grid(row=1, column=0, columnspan=4, sticky="we", pady=(2, 10))

        e = self.engine
        rows = [
            [
                ("MC", e.memory_clear, MEM),
                ("MR", e.memory_recall, MEM),
                ("M+", e.memory_add, MEM),
                ("M−", e.memory_subtract, MEM),
            ],
            [
                ("AC", e.all_clear, UTIL),
                ("C", e.clear_entry, UTIL),
                ("⌫", e.backspace, UTIL),
                ("÷", lambda: e.set_operator("/"), OP),
            ],
            [
                ("x²", e.square, FUNC),
                ("√", e.square_root, FUNC),
                ("1/x", e.reciprocal, FUNC),
                ("×", lambda: e.set_operator("*"), OP),
            ],
            [
                ("7", lambda: e.input_digit("7"), NUM),
                ("8", lambda: e.input_digit("8"), NUM),
                ("9", lambda: e.input_digit("9"), NUM),
                ("−", lambda: e.set_operator("-"), OP),
            ],
            [
                ("4", lambda: e.input_digit("4"), NUM),
                ("5", lambda: e.input_digit("5"), NUM),
                ("6", lambda: e.input_digit("6"), NUM),
                ("+", lambda: e.set_operator("+"), OP),
            ],
            [
                ("1", lambda: e.input_digit("1"), NUM),
                ("2", lambda: e.input_digit("2"), NUM),
                ("3", lambda: e.input_digit("3"), NUM),
                ("=", self._equals_and_record, EQ),
            ],
            [
                ("±", e.negate, FUNC),
                ("0", lambda: e.input_digit("0"), NUM),
                (".", e.input_dot, NUM),
                ("%", e.percent, FUNC),
            ],
        ]
        for r, row in enumerate(rows, start=2):
            for c, (label, action, style) in enumerate(row):
                ttk.Button(
                    self,
                    text=label,
                    bootstyle=style,
                    command=self._wrap(action),
                    width=5,
                ).grid(row=r, column=c, sticky="nsew", padx=2, pady=2)

        for c in range(4):
            self.columnconfigure(c, weight=1)
        for r in range(2, len(rows) + 2):
            self.rowconfigure(r, weight=1)

    def _wrap(self, action):
        def handler():
            action()
            self._refresh()

        return handler

    def _refresh(self) -> None:
        self._display_var.set(self.engine.display)
        flags = []
        if self.engine.memory.has_value:
            flags.append("M")
        if self.engine.grand_total.total:
            flags.append(f"GT={self.engine.grand_total.total:g}")
        self._status_var.set("   ".join(flags))

    def on_key(self, event: tk.Event) -> None:
        key, char = event.keysym, event.char
        if char in _KEY_TO_DIGIT:
            self.engine.input_digit(char)
        elif char in "+-*/":
            self.engine.set_operator(char)
        elif char == ".":
            self.engine.input_dot()
        elif char == "%":
            self.engine.percent()
        elif key in ("Return", "equal", "KP_Enter"):
            self._equals_and_record()
        elif key == "BackSpace":
            self.engine.backspace()
        elif key == "Escape":
            self.engine.all_clear()
        else:
            return
        self._refresh()
