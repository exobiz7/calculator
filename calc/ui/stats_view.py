"""Tkinter view for the statistics / distribution mode."""

import tkinter as tk

import ttkbootstrap as ttk

from calc.core.numfmt import format_value
from calc.modes import stats

MODES = ["기술통계", "회귀(선형)", "정규분포", "이항분포"]


def _f(text: str, default: float = 0.0) -> float:
    text = text.replace(",", "").strip()
    return float(text) if text else default


class StatsView(ttk.Frame):
    def __init__(self, master: tk.Misc, on_record=None) -> None:
        super().__init__(master, padding=10)
        self._on_record = on_record
        self._widgets: dict[str, object] = {}
        self._build()

    def _build(self) -> None:
        top = ttk.Frame(self)
        top.pack(fill="x")
        ttk.Label(top, text="모드").pack(side="left", padx=(0, 6))
        self._mode = ttk.Combobox(top, values=MODES, state="readonly", width=14)
        self._mode.pack(side="left")
        self._mode.bind("<<ComboboxSelected>>", lambda e: self._render_inputs())

        self._inputs = ttk.Frame(self, padding=(0, 8))
        self._inputs.pack(fill="x")

        ttk.Button(self, text="계산", bootstyle="primary", command=self._compute).pack(
            fill="x", pady=4
        )

        cols = ("항목", "값")
        self._tree = ttk.Treeview(self, columns=cols, show="headings", height=10)
        self._tree.heading("항목", text="항목")
        self._tree.heading("값", text="값")
        self._tree.column("항목", width=140, anchor="w")
        self._tree.column("값", width=180, anchor="e")
        self._tree.pack(fill="both", expand=True, pady=(6, 0))

        self._mode.current(0)
        self._render_inputs()

    # --- input layouts --------------------------------------------------
    def _add_text(self, parent, label, row, height=3):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="nw", pady=2)
        txt = tk.Text(parent, height=height, width=30)
        txt.grid(row=row, column=1, sticky="we", pady=2, padx=(8, 0))
        return txt

    def _add_entry(self, parent, label, row, default=""):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=2)
        sv = tk.StringVar(value=default)
        ttk.Entry(parent, textvariable=sv, width=16).grid(
            row=row, column=1, sticky="we", pady=2, padx=(8, 0)
        )
        return sv

    def _render_inputs(self) -> None:
        for w in self._inputs.winfo_children():
            w.destroy()
        self._widgets = {}
        mode = self._mode.get()
        f = self._inputs
        if mode == "기술통계":
            self._widgets["data"] = self._add_text(f, "데이터", 0)
        elif mode == "회귀(선형)":
            self._widgets["x"] = self._add_text(f, "x 값", 0, height=2)
            self._widgets["y"] = self._add_text(f, "y 값", 1, height=2)
        elif mode == "정규분포":
            self._widgets["x"] = self._add_entry(f, "x (또는 확률 p)", 0)
            self._widgets["mu"] = self._add_entry(f, "평균 μ", 1, "0")
            self._widgets["sigma"] = self._add_entry(f, "표준편차 σ", 2, "1")
            self._widgets["func"] = self._combo(f, "함수", 3, ["pdf", "cdf", "역(inv)"])
        elif mode == "이항분포":
            self._widgets["k"] = self._add_entry(f, "성공 k", 0)
            self._widgets["n"] = self._add_entry(f, "시행 n", 1)
            self._widgets["p"] = self._add_entry(f, "확률 p", 2, "0.5")
            self._widgets["func"] = self._combo(f, "함수", 3, ["pmf", "cdf"])
        f.columnconfigure(1, weight=1)
        self._clear_results()

    def _combo(self, parent, label, row, values):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=2)
        cb = ttk.Combobox(parent, values=values, state="readonly", width=14)
        cb.current(0)
        cb.grid(row=row, column=1, sticky="w", pady=2, padx=(8, 0))
        return cb

    # --- compute --------------------------------------------------------
    def _clear_results(self) -> None:
        self._tree.delete(*self._tree.get_children())

    def _show_rows(self, rows: list[tuple[str, str]]) -> None:
        self._clear_results()
        for k, v in rows:
            self._tree.insert("", "end", values=(k, v))

    def _text(self, key) -> str:
        return self._widgets[key].get("1.0", "end")

    def _compute(self) -> None:
        mode = self._mode.get()
        try:
            rows, desc, inputs = self._dispatch(mode)
        except ValueError as e:
            self._show_rows([("오류", str(e))])
            return
        self._show_rows(rows)
        if self._on_record and rows:
            self._on_record(desc, rows[0][1], inputs)

    def _dispatch(self, mode):
        if mode == "기술통계":
            raw = self._text("data")
            data = stats.parse_list(raw)
            d = stats.describe(data)
            rows = [
                (k, v if isinstance(v, str) else format_value(float(v)))
                for k, v in d.items()
            ]
            return rows, f"기술통계 (n={d['n']})", {"mode": mode, "data": raw}
        if mode == "회귀(선형)":
            xr, yr = self._text("x"), self._text("y")
            r = stats.linreg(stats.parse_list(xr), stats.parse_list(yr))
            rows = [(k, format_value(v)) for k, v in r.items()]
            return (
                rows,
                f"회귀 기울기 {format_value(r['기울기'])}",
                {"mode": mode, "x": xr, "y": yr},
            )
        if mode == "정규분포":
            x = _f(self._widgets["x"].get())
            mu, sigma = (
                _f(self._widgets["mu"].get()),
                _f(self._widgets["sigma"].get(), 1),
            )
            fn = self._widgets["func"].get()
            if fn == "pdf":
                val = stats.normal_pdf(x, mu, sigma)
            elif fn == "cdf":
                val = stats.normal_cdf(x, mu, sigma)
            else:
                val = stats.normal_inv(x, mu, sigma)
            res = format_value(val)
            return (
                [("결과", res), ("함수", fn)],
                f"정규 {fn}({x:g})",
                {
                    "mode": mode,
                    "x": self._widgets["x"].get(),
                    "mu": self._widgets["mu"].get(),
                    "sigma": self._widgets["sigma"].get(),
                    "func": fn,
                },
            )
        # 이항분포
        k = int(_f(self._widgets["k"].get()))
        n = int(_f(self._widgets["n"].get()))
        p = _f(self._widgets["p"].get(), 0.5)
        fn = self._widgets["func"].get()
        val = stats.binom_pmf(k, n, p) if fn == "pmf" else stats.binom_cdf(k, n, p)
        res = format_value(val)
        return (
            [("결과", res), ("함수", fn)],
            f"이항 {fn}(k={k},n={n})",
            {
                "mode": mode,
                "k": self._widgets["k"].get(),
                "n": self._widgets["n"].get(),
                "p": self._widgets["p"].get(),
                "func": fn,
            },
        )

    # --- history reuse --------------------------------------------------
    def load(self, entry) -> None:
        inp = entry.inputs
        mode = inp.get("mode")
        if mode not in MODES:
            return
        self._mode.set(mode)
        self._render_inputs()
        for key, w in self._widgets.items():
            if key not in inp:
                continue
            if isinstance(w, tk.Text):
                w.delete("1.0", "end")
                w.insert("1.0", inp[key])
            elif isinstance(w, ttk.Combobox):
                w.set(inp[key])
            else:  # StringVar
                w.set(inp[key])
        self._compute()

    def on_key(self, event: tk.Event) -> None:
        return
