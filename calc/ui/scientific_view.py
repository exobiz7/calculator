"""Tkinter view for the scientific calculator mode (expression entry)."""

import tkinter as tk

import ttkbootstrap as ttk

from calc.core.numfmt import MODES, format_value
from calc.modes.basic import format_number
from calc.modes.scientific import ScientificEngine
from calc.ui.basic_view import EQ, FUNC, NUM, OP, UTIL

SEC = "secondary-outline"


class ScientificView(ttk.Frame):
    def __init__(self, master: tk.Misc, on_record=None) -> None:
        super().__init__(master, padding=10)
        self.engine = ScientificEngine()
        self._on_record = on_record
        self._expr_var = tk.StringVar(value="")
        self._result_var = tk.StringVar(value="0")
        self._angle_var = tk.StringVar(value=self.engine.angle)
        self._fmt_var = tk.StringVar(value="자동")
        self._build()
        # Live result: re-evaluate (without recording) as the expression changes.
        self._expr_var.trace_add("write", self._on_expr_change)

    def load_expression(self, entry) -> None:
        """Populate the entry field from a history entry (for re-use)."""
        self._expr_var.set(entry.expression)
        self._result_var.set("0")

    def _build(self) -> None:
        top = ttk.Frame(self)
        top.grid(row=0, column=0, columnspan=5, sticky="we")
        ttk.Button(
            top,
            textvariable=self._angle_var,
            width=6,
            bootstyle="info",
            command=self._toggle_angle,
        ).pack(side="left")
        fmt = ttk.Combobox(
            top, textvariable=self._fmt_var, values=MODES, state="readonly", width=6
        )
        fmt.pack(side="left", padx=(6, 0))
        fmt.bind("<<ComboboxSelected>>", lambda e: self._show_result())
        ttk.Button(
            top, text="복사", width=4, bootstyle=SEC, command=self._copy_result
        ).pack(side="left", padx=(6, 0))
        ttk.Button(
            top, text="식복사", width=5, bootstyle=SEC, command=self._copy_expr
        ).pack(side="left", padx=(2, 0))
        ttk.Label(
            top,
            textvariable=self._result_var,
            anchor="e",
            font=("Helvetica", 22, "bold"),
        ).pack(side="right", fill="x", expand=True)

        ttk.Entry(self, textvariable=self._expr_var, font=("Helvetica", 18)).grid(
            row=1, column=0, columnspan=5, sticky="we", pady=(6, 10)
        )

        # (label, token, bootstyle)
        rows = [
            [
                ("Ans", "@ans", SEC),
                ("(", "(", SEC),
                (")", ")", SEC),
                ("⌫", "@back", UTIL),
                ("C", "@clear", UTIL),
            ],
            [
                ("sin", "sin(", FUNC),
                ("cos", "cos(", FUNC),
                ("tan", "tan(", FUNC),
                ("xʸ", "**", OP),
                ("√", "sqrt(", FUNC),
            ],
            [
                ("ln", "ln(", FUNC),
                ("log", "log(", FUNC),
                ("π", "pi", FUNC),
                ("e", "e", FUNC),
                ("n!", "fact(", FUNC),
            ],
            [
                ("7", "7", NUM),
                ("8", "8", NUM),
                ("9", "9", NUM),
                ("÷", "/", OP),
                ("x²", "**2", FUNC),
            ],
            [
                ("4", "4", NUM),
                ("5", "5", NUM),
                ("6", "6", NUM),
                ("×", "*", OP),
                ("∛", "cbrt(", FUNC),
            ],
            [
                ("1", "1", NUM),
                ("2", "2", NUM),
                ("3", "3", NUM),
                ("−", "-", OP),
                ("asin", "asin(", FUNC),
            ],
            [
                ("0", "0", NUM),
                (".", ".", NUM),
                ("+", "+", OP),
                ("=", "@eval", EQ),
                ("acos", "acos(", FUNC),
            ],
        ]
        for r, row in enumerate(rows, start=2):
            for c, (label, token, style) in enumerate(row):
                ttk.Button(
                    self,
                    text=label,
                    bootstyle=style,
                    width=5,
                    command=lambda t=token: self._press(t),
                ).grid(row=r, column=c, sticky="nsew", padx=2, pady=2)

        for c in range(5):
            self.columnconfigure(c, weight=1)
        for r in range(2, len(rows) + 2):
            self.rowconfigure(r, weight=1)

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
        self._compute(record=False)

    def _show_result(self) -> None:
        if self.engine.error or not self._expr_var.get().strip():
            self._result_var.set("")  # silent while typing / empty
        else:
            self._result_var.set(
                format_value(self.engine.last_answer, self._fmt_var.get())
            )

    def _compute(self, record: bool) -> None:
        self.engine.expression = self._expr_var.get()
        self.engine.evaluate()
        self._show_result()
        if (
            record
            and self._on_record
            and not self.engine.error
            and self.engine.expression.strip()
        ):
            self._on_record(self.engine.expression, self._result_var.get())

    def _on_expr_change(self, *args) -> None:
        self._compute(record=False)

    def _evaluate(self) -> None:
        self._compute(record=True)
        if self.engine.error and self._expr_var.get().strip():
            self._result_var.set("Error")  # explicit "=" surfaces the error

    def _copy_result(self) -> None:
        self.clipboard_clear()
        self.clipboard_append(self._result_var.get())

    def _copy_expr(self) -> None:
        self.clipboard_clear()
        self.clipboard_append(self._expr_var.get())

    def on_key(self, event: tk.Event) -> None:
        if event.keysym in ("Return", "KP_Enter"):
            self._evaluate()
