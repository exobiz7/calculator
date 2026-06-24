"""Tkinter view for the scientific calculator mode (expression entry)."""

import tkinter as tk
from tkinter import ttk

from calc.modes.basic import format_number
from calc.modes.scientific import ScientificEngine


class ScientificView(ttk.Frame):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, padding=8)
        self.engine = ScientificEngine()
        self._expr_var = tk.StringVar(value="")
        self._result_var = tk.StringVar(value="0")
        self._angle_var = tk.StringVar(value=self.engine.angle)
        self._build()

    def _build(self) -> None:
        top = ttk.Frame(self)
        top.grid(row=0, column=0, columnspan=5, sticky="we")
        ttk.Button(
            top, textvariable=self._angle_var, width=6, command=self._toggle_angle
        ).pack(side="left")
        ttk.Label(
            top, textvariable=self._result_var, anchor="e", font=("Helvetica", 20)
        ).pack(side="right", fill="x", expand=True)

        entry = ttk.Entry(self, textvariable=self._expr_var, font=("Helvetica", 18))
        entry.grid(row=1, column=0, columnspan=5, sticky="we", pady=(4, 8))
        entry.bind("<Return>", lambda e: self._evaluate())

        # token: text inserted into the expression (or special handler key)
        rows = [
            [("Ans", "@ans"), ("(", "("), (")", ")"), ("⌫", "@back"), ("C", "@clear")],
            [
                ("sin", "sin("),
                ("cos", "cos("),
                ("tan", "tan("),
                ("xʸ", "**"),
                ("√", "sqrt("),
            ],
            [("ln", "ln("), ("log", "log("), ("π", "pi"), ("e", "e"), ("n!", "fact(")],
            [("7", "7"), ("8", "8"), ("9", "9"), ("÷", "/"), ("x²", "**2")],
            [("4", "4"), ("5", "5"), ("6", "6"), ("×", "*"), ("∛", "cbrt(")],
            [("1", "1"), ("2", "2"), ("3", "3"), ("−", "-"), ("asin", "asin(")],
            [("0", "0"), (".", "."), ("+", "+"), ("=", "@eval"), ("acos", "acos(")],
        ]
        for r, row in enumerate(rows, start=2):
            for c, (label, token) in enumerate(row):
                ttk.Button(
                    self, text=label, width=5, command=lambda t=token: self._press(t)
                ).grid(row=r, column=c, sticky="nsew", padx=1, pady=1)

        for c in range(5):
            self.columnconfigure(c, weight=1)
        for r in range(2, len(rows) + 2):
            self.rowconfigure(r, weight=1)

    # --- actions --------------------------------------------------------
    def _press(self, token: str) -> None:
        if token == "@eval":
            self._evaluate()
        elif token == "@back":
            self._expr_var.set(self._expr_var.get()[:-1])
        elif token == "@clear":
            self._expr_var.set("")
            self._result_var.set("0")
        elif token == "@ans":
            self._expr_var.set(
                self._expr_var.get() + format_number(self.engine.last_answer)
            )
        else:
            self._expr_var.set(self._expr_var.get() + token)

    def _toggle_angle(self) -> None:
        self._angle_var.set(self.engine.toggle_angle())

    def _evaluate(self) -> None:
        self.engine.expression = self._expr_var.get()
        self._result_var.set(self.engine.evaluate())

    # --- keyboard -------------------------------------------------------
    def on_key(self, event: tk.Event) -> None:
        # The Entry handles text natively; only intercept Enter for eval.
        if event.keysym in ("Return", "KP_Enter"):
            self._evaluate()
