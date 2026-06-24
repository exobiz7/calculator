"""Tkinter view for the graphing mode (matplotlib embedded)."""

import tkinter as tk

import ttkbootstrap as ttk

from calc.core.plotting import sample

try:  # graceful if matplotlib isn't installed
    import matplotlib

    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import (
        FigureCanvasTkAgg,
        NavigationToolbar2Tk,
    )
    from matplotlib.figure import Figure

    _HAS_MPL = True
except Exception:  # pragma: no cover - exercised only without matplotlib
    _HAS_MPL = False

COLORS = ["#d97757", "#6a9bcc", "#788c5d"]  # clay / blue / green


def _f(text: str, default: float = 0.0) -> float:
    text = text.replace(",", "").strip()
    return float(text) if text else default


class GraphView(ttk.Frame):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, padding=10)
        self._angle_var = tk.StringVar(value="RAD")
        self._status_var = tk.StringVar(value="")
        self._fn_vars: list[tk.StringVar] = []
        if not _HAS_MPL:
            ttk.Label(
                self,
                text="matplotlib가 설치되어 있지 않습니다.\n"
                "pip install matplotlib 후 사용하세요.",
                bootstyle="warning",
                justify="center",
            ).pack(expand=True)
            return
        self._build()

    def _build(self) -> None:
        ctrl = ttk.Frame(self)
        ctrl.pack(fill="x")
        for i, color in enumerate(COLORS):
            ttk.Label(ctrl, text=f"f{i + 1}(x) =", foreground=color).grid(
                row=i, column=0, sticky="w", pady=1
            )
            sv = tk.StringVar(value="5*x**2 + cos(x)" if i == 0 else "")
            ttk.Entry(ctrl, textvariable=sv).grid(
                row=i, column=1, columnspan=3, sticky="we", pady=1, padx=(6, 0)
            )
            self._fn_vars.append(sv)

        ttk.Label(ctrl, text="x 범위").grid(row=3, column=0, sticky="w", pady=(6, 0))
        self._xmin = tk.StringVar(value="-10")
        self._xmax = tk.StringVar(value="10")
        ttk.Entry(ctrl, textvariable=self._xmin, width=8).grid(
            row=3, column=1, sticky="w", pady=(6, 0)
        )
        ttk.Label(ctrl, text="~").grid(row=3, column=2, pady=(6, 0))
        ttk.Entry(ctrl, textvariable=self._xmax, width=8).grid(
            row=3, column=3, sticky="w", pady=(6, 0)
        )
        ctrl.columnconfigure(1, weight=1)

        btns = ttk.Frame(self)
        btns.pack(fill="x", pady=4)
        ttk.Button(btns, text="그리기", bootstyle="primary", command=self.plot).pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(
            btns,
            textvariable=self._angle_var,
            width=6,
            bootstyle="info",
            command=self._toggle_angle,
        ).pack(side="left", padx=(6, 0))
        ttk.Label(self, textvariable=self._status_var, bootstyle="danger").pack(
            anchor="w"
        )

        self._fig = Figure(figsize=(5, 3.6), dpi=100)
        self._ax = self._fig.add_subplot(111)
        self._canvas = FigureCanvasTkAgg(self._fig, master=self)
        self._canvas.get_tk_widget().pack(fill="both", expand=True)
        toolbar = NavigationToolbar2Tk(self._canvas, self, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(fill="x")
        self.plot()

    def _toggle_angle(self) -> None:
        self._angle_var.set("DEG" if self._angle_var.get() == "RAD" else "RAD")
        self.plot()

    def plot(self) -> None:
        if not _HAS_MPL:
            return
        self._status_var.set("")
        try:
            xmin, xmax = _f(self._xmin.get(), -10), _f(self._xmax.get(), 10)
            self._ax.clear()
            self._ax.axhline(0, color="#999", linewidth=0.8)
            self._ax.axvline(0, color="#999", linewidth=0.8)
            self._ax.grid(True, alpha=0.3)
            plotted = False
            for sv, color in zip(self._fn_vars, COLORS):
                expr = sv.get().strip()
                if not expr:
                    continue
                xs, ys = sample(expr, xmin, xmax, self._angle_var.get())
                self._ax.plot(xs, ys, color=color, label=f"y={expr}")
                plotted = True
            if plotted:
                self._ax.legend(fontsize=8, loc="best")
            self._canvas.draw()
        except ValueError as e:
            self._status_var.set(f"오류: {e}")

    def on_key(self, event: tk.Event) -> None:
        return
