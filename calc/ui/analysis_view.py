"""Tkinter view for numerical analysis: derivative, integral, root finding."""

import tkinter as tk

import ttkbootstrap as ttk

from calc.core.numeric import integrate, nderiv, solve
from calc.core.numfmt import format_value

# op label -> (parameter (key, label) list)
OPS = {
    "미분 f'(x₀)": (("x0", "x₀"),),
    "정적분 ∫f dx": (("a", "하한 a"), ("b", "상한 b")),
    "방정식 근 f(x)=0": (("guess", "초기값"),),
}


def _to_float(text: str, default: float = 0.0) -> float:
    text = text.replace(",", "").strip()
    return float(text) if text else default


class AnalysisView(ttk.Frame):
    def __init__(self, master: tk.Misc, on_record=None) -> None:
        super().__init__(master, padding=10)
        self._on_record = on_record
        self._expr_var = tk.StringVar(value="x**2")
        self._result_var = tk.StringVar(value="")
        self._angle_var = tk.StringVar(value="RAD")
        self._params: dict[str, tk.StringVar] = {}
        self._build()

    def _build(self) -> None:
        top = ttk.Frame(self)
        top.pack(fill="x")
        ttk.Label(top, text="연산").pack(side="left", padx=(0, 6))
        self._op = ttk.Combobox(top, values=list(OPS), state="readonly", width=18)
        self._op.pack(side="left")
        self._op.bind("<<ComboboxSelected>>", lambda e: self._render_params())
        ttk.Button(
            top,
            textvariable=self._angle_var,
            width=6,
            bootstyle="info",
            command=self._toggle_angle,
        ).pack(side="right")

        fexpr = ttk.Frame(self, padding=(0, 8))
        fexpr.pack(fill="x")
        ttk.Label(fexpr, text="f(x) =").pack(side="left")
        ttk.Entry(fexpr, textvariable=self._expr_var, font=("Helvetica", 14)).pack(
            side="left", fill="x", expand=True, padx=6
        )

        self._pframe = ttk.Frame(self)
        self._pframe.pack(fill="x")

        ttk.Button(self, text="계산", bootstyle="primary", command=self._compute).pack(
            fill="x", pady=4
        )
        ttk.Label(
            self,
            textvariable=self._result_var,
            bootstyle="success",
            font=("Helvetica", 20, "bold"),
        ).pack(anchor="w", pady=(6, 0))

        self._op.current(0)
        self._render_params()

    def _toggle_angle(self) -> None:
        self._angle_var.set("DEG" if self._angle_var.get() == "RAD" else "RAD")

    def _render_params(self) -> None:
        for w in self._pframe.winfo_children():
            w.destroy()
        self._params = {}
        defaults = {"x0": "1", "a": "0", "b": "1", "guess": "1"}
        for r, (key, label) in enumerate(OPS[self._op.get()]):
            ttk.Label(self._pframe, text=label).grid(
                row=r, column=0, sticky="w", pady=2
            )
            sv = tk.StringVar(value=defaults.get(key, ""))
            ttk.Entry(self._pframe, textvariable=sv, width=16).grid(
                row=r, column=1, sticky="we", pady=2, padx=(8, 0)
            )
            self._params[key] = sv
        self._pframe.columnconfigure(1, weight=1)
        self._result_var.set("")

    def _compute(self) -> None:
        op = self._op.get()
        expr = self._expr_var.get()
        angle = self._angle_var.get()
        try:
            if op.startswith("미분"):
                x0 = _to_float(self._params["x0"].get())
                value = nderiv(expr, x0, angle)
                desc = f"d/dx[{expr}] @ x={x0:g}"
            elif op.startswith("정적분"):
                a, b = (
                    _to_float(self._params["a"].get()),
                    _to_float(self._params["b"].get()),
                )
                value = integrate(expr, a, b, angle)
                desc = f"∫[{a:g},{b:g}] {expr} dx"
            else:  # 방정식 근
                guess = _to_float(self._params["guess"].get(), 1.0)
                value = solve(expr, angle, guess=guess)
                desc = f"solve {expr}=0 (x₀={guess:g})"
        except (ValueError, ZeroDivisionError, OverflowError) as e:
            self._result_var.set(f"오류: {e}")
            return
        text = format_value(value, "자동")
        self._result_var.set(text)
        if self._on_record:
            self._on_record(
                desc,
                text,
                {
                    "op": op,
                    "expr": expr,
                    "angle": angle,
                    **{k: v.get() for k, v in self._params.items()},
                },
            )

    def load(self, entry) -> None:
        inp = entry.inputs
        op = inp.get("op")
        if op not in OPS:
            return
        self._op.set(op)
        self._render_params()
        self._expr_var.set(inp.get("expr", ""))
        self._angle_var.set(inp.get("angle", "RAD"))
        for key, sv in self._params.items():
            if key in inp:
                sv.set(str(inp[key]))
        self._compute()

    def on_key(self, event: tk.Event) -> None:
        if event.keysym in ("Return", "KP_Enter"):
            self._compute()
