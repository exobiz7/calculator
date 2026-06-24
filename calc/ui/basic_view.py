"""Tkinter view for the basic calculator mode."""

import tkinter as tk
from tkinter import ttk

from calc.modes.basic import CalculatorEngine

# (label, callback-name-or-handler, style)
_KEY_TO_DIGIT = set("0123456789")


class BasicView(ttk.Frame):
    """Button grid + display wired to a CalculatorEngine."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, padding=8)
        self.engine = CalculatorEngine()
        self._display_var = tk.StringVar(value="0")
        self._status_var = tk.StringVar(value="")
        self._build()
        self._refresh()

    # --- layout ---------------------------------------------------------
    def _build(self) -> None:
        status = ttk.Label(
            self, textvariable=self._status_var, anchor="w", foreground="#888"
        )
        status.grid(row=0, column=0, columnspan=4, sticky="we")

        display = ttk.Label(
            self,
            textvariable=self._display_var,
            anchor="e",
            font=("Helvetica", 28),
            relief="sunken",
            padding=8,
        )
        display.grid(row=1, column=0, columnspan=4, sticky="we", pady=(2, 8))

        rows = [
            [
                ("MC", self.engine.memory_clear),
                ("MR", self.engine.memory_recall),
                ("M+", self.engine.memory_add),
                ("M−", self.engine.memory_subtract),
            ],
            [
                ("AC", self.engine.all_clear),
                ("C", self.engine.clear_entry),
                ("⌫", self.engine.backspace),
                ("÷", lambda: self.engine.set_operator("/")),
            ],
            [
                ("x²", self.engine.square),
                ("√", self.engine.square_root),
                ("1/x", self.engine.reciprocal),
                ("×", lambda: self.engine.set_operator("*")),
            ],
            [
                ("7", lambda: self.engine.input_digit("7")),
                ("8", lambda: self.engine.input_digit("8")),
                ("9", lambda: self.engine.input_digit("9")),
                ("−", lambda: self.engine.set_operator("-")),
            ],
            [
                ("4", lambda: self.engine.input_digit("4")),
                ("5", lambda: self.engine.input_digit("5")),
                ("6", lambda: self.engine.input_digit("6")),
                ("+", lambda: self.engine.set_operator("+")),
            ],
            [
                ("1", lambda: self.engine.input_digit("1")),
                ("2", lambda: self.engine.input_digit("2")),
                ("3", lambda: self.engine.input_digit("3")),
                ("=", self.engine.equals),
            ],
            [
                ("±", self.engine.negate),
                ("0", lambda: self.engine.input_digit("0")),
                (".", self.engine.input_dot),
                ("%", self.engine.percent),
            ],
        ]
        for r, row in enumerate(rows, start=2):
            for c, (label, action) in enumerate(row):
                btn = ttk.Button(self, text=label, width=5, command=self._wrap(action))
                btn.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)

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
        self._status_var.set("  ".join(flags))

    # --- keyboard (routed here by the app when this tab is active) -------
    def on_key(self, event: tk.Event) -> None:
        key = event.keysym
        char = event.char
        if char in _KEY_TO_DIGIT:
            self.engine.input_digit(char)
        elif char in "+-*/":
            self.engine.set_operator(char)
        elif char == ".":
            self.engine.input_dot()
        elif char == "%":
            self.engine.percent()
        elif key in ("Return", "equal", "KP_Enter"):
            self.engine.equals()
        elif key == "BackSpace":
            self.engine.backspace()
        elif key == "Escape":
            self.engine.all_clear()
        else:
            return
        self._refresh()
