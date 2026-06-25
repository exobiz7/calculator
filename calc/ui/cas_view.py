"""Tkinter view for the CAS (symbolic math) mode."""

import threading
import tkinter as tk

import ttkbootstrap as ttk

try:  # graceful if sympy isn't installed
    from calc.modes import cas

    _HAS_CAS = True
except Exception:  # pragma: no cover - only without sympy
    _HAS_CAS = False

# op -> parameter (key, label, default) list
_PARAMS = {
    "미분": (("var", "변수", "x"), ("n", "차수", "1")),
    "부정적분": (("var", "변수", "x"),),
    "정적분": (("var", "변수", "x"), ("a", "하한", "0"), ("b", "상한", "1")),
    "극한": (("var", "변수", "x"), ("point", "→", "0")),
}
_TIMEOUT = 5.0


class CASView(ttk.Frame):
    def __init__(self, master: tk.Misc, on_record=None) -> None:
        super().__init__(master, padding=10)
        self._on_record = on_record
        self._expr_var = tk.StringVar(value="x**2")
        self._result_var = tk.StringVar(value="")
        self._status_var = tk.StringVar(value="")
        self._params: dict[str, tk.StringVar] = {}
        self._exact = ""
        self._approx = ""
        self._numeric = False  # S↔D state (False=정확값, True=수치)
        if not _HAS_CAS:
            ttk.Label(
                self,
                text="sympy가 설치되어 있지 않습니다.\n"
                "pip install sympy 후 사용하세요.",
                bootstyle="warning",
                justify="center",
            ).pack(expand=True)
            return
        self._build()

    def _build(self) -> None:
        top = ttk.Frame(self)
        top.pack(fill="x")
        ttk.Label(top, text="연산").pack(side="left", padx=(0, 6))
        self._op = ttk.Combobox(top, values=cas.OPS, state="readonly", width=10)
        self._op.pack(side="left")
        self._op.bind("<<ComboboxSelected>>", lambda e: self._render_params())

        fexpr = ttk.Frame(self, padding=(0, 8))
        fexpr.pack(fill="x")
        ttk.Label(fexpr, text="식").pack(side="left")
        ttk.Entry(fexpr, textvariable=self._expr_var, font=("Helvetica", 14)).pack(
            side="left", fill="x", expand=True, padx=6
        )

        self._pframe = ttk.Frame(self)
        self._pframe.pack(fill="x")

        btns = ttk.Frame(self)
        btns.pack(fill="x", pady=4)
        ttk.Button(btns, text="계산", bootstyle="primary", command=self._compute).pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(
            btns, text="S↔D", width=6, bootstyle="info", command=self._toggle_sd
        ).pack(side="left", padx=(6, 0))
        ttk.Button(
            btns,
            text="복사",
            width=5,
            bootstyle="secondary-outline",
            command=self._copy,
        ).pack(side="left", padx=(2, 0))

        ttk.Label(
            self,
            textvariable=self._result_var,
            bootstyle="success",
            font=("Helvetica", 18, "bold"),
            wraplength=360,
        ).pack(anchor="w", pady=(6, 0))
        ttk.Label(self, textvariable=self._status_var, bootstyle="secondary").pack(
            anchor="w"
        )

        self._op.current(0)
        self._render_params()

    def _render_params(self) -> None:
        for w in self._pframe.winfo_children():
            w.destroy()
        self._params = {}
        for r, (key, label, default) in enumerate(_PARAMS.get(self._op.get(), ())):
            ttk.Label(self._pframe, text=label).grid(
                row=r, column=0, sticky="w", pady=2
            )
            sv = tk.StringVar(value=default)
            ttk.Entry(self._pframe, textvariable=sv, width=12).grid(
                row=r, column=1, sticky="w", pady=2, padx=(8, 0)
            )
            self._params[key] = sv

    def _toggle_sd(self) -> None:
        self._numeric = not self._numeric
        self._show()

    def _show(self) -> None:
        self._result_var.set(self._approx if self._numeric else self._exact)

    def _compute(self) -> None:
        op = self._op.get()
        expr = self._expr_var.get()
        kw = {k: v.get() for k, v in self._params.items()}
        self._status_var.set("계산 중…")
        self.update_idletasks()

        box: dict = {}

        def work():
            try:
                box["ok"] = cas.compute(op, expr, **kw)
            except Exception as exc:  # surface any sympy error as a message
                box["err"] = str(exc)

        t = threading.Thread(target=work, daemon=True)
        t.start()
        t.join(_TIMEOUT)
        if t.is_alive():
            self._status_var.set("시간 초과 (식을 단순화해 보세요)")
            return
        if "err" in box:
            self._status_var.set(f"오류: {box['err']}")
            self._exact = self._approx = ""
            self._result_var.set("")
            return
        self._exact, self._approx = box["ok"]
        self._numeric = False
        self._status_var.set("")
        self._show()
        if self._on_record:
            self._on_record(
                f"{op}: {expr}", self._exact, {"op": op, "expr": expr, **kw}
            )

    def _copy(self) -> None:
        self.clipboard_clear()
        self.clipboard_append(self._result_var.get())

    def load(self, entry) -> None:
        inp = entry.inputs
        op = inp.get("op")
        if op not in cas.OPS:
            return
        self._op.set(op)
        self._render_params()
        self._expr_var.set(inp.get("expr", ""))
        for key, sv in self._params.items():
            if key in inp:
                sv.set(str(inp[key]))
        self._compute()

    def on_key(self, event: tk.Event) -> None:
        if event.keysym in ("Return", "KP_Enter"):
            self._compute()
