"""Tkinter view for the managerial-accounting KPI mode."""

import tkinter as tk

import ttkbootstrap as ttk

from calc.modes import kpi as kpimod
from calc.modes.kpi import KPI_BY_KEY, compute


def _to_float(text: str) -> float:
    text = text.replace(",", "").strip()
    return float(text) if text else 0.0


class KPIView(ttk.Frame):
    def __init__(self, master: tk.Misc, on_record=None) -> None:
        super().__init__(master, padding=10)
        self._on_record = on_record
        self._current = None  # selected KPI
        self._vars: dict[str, tk.StringVar] = {}
        self._result_var = tk.StringVar(value="")
        self._note_var = tk.StringVar(value="")
        self._build()

    def _build(self) -> None:
        sel = ttk.Frame(self)
        sel.pack(fill="x")
        ttk.Label(sel, text="분류").grid(row=0, column=0, sticky="w", padx=(0, 6))
        self._cat = ttk.Combobox(
            sel, values=kpimod.CATEGORIES, state="readonly", width=14
        )
        self._cat.grid(row=0, column=1, sticky="w")
        self._cat.bind("<<ComboboxSelected>>", lambda e: self._on_category())
        ttk.Label(sel, text="지표").grid(row=0, column=2, sticky="w", padx=(12, 6))
        self._metric = ttk.Combobox(sel, state="readonly", width=24)
        self._metric.grid(row=0, column=3, sticky="we")
        self._metric.bind("<<ComboboxSelected>>", lambda e: self._on_metric())
        sel.columnconfigure(3, weight=1)

        self._inputs = ttk.Frame(self, padding=(0, 10))
        self._inputs.pack(fill="x")

        self._calc_btn = ttk.Button(
            self,
            text="계산",
            bootstyle="primary",
            command=self._compute,
            state="disabled",
        )
        self._calc_btn.pack(fill="x", pady=4)

        ttk.Label(
            self,
            textvariable=self._result_var,
            bootstyle="success",
            font=("Helvetica", 18, "bold"),
        ).pack(anchor="w", pady=(6, 0))
        ttk.Label(
            self, textvariable=self._note_var, bootstyle="secondary", wraplength=320
        ).pack(anchor="w")

        self._cat.current(0)
        self._on_category()

    # --- selection ------------------------------------------------------
    def _on_category(self) -> None:
        names = [k.name for k in kpimod.by_category(self._cat.get())]
        self._metric.configure(values=names)
        if names:
            self._metric.current(0)
            self._on_metric()

    def _name_to_kpi(self, name: str):
        for k in kpimod.by_category(self._cat.get()):
            if k.name == name:
                return k
        return None

    def _on_metric(self) -> None:
        kpi = self._name_to_kpi(self._metric.get())
        if kpi is None:
            return
        self._current = kpi
        self._render_inputs(kpi)
        self._result_var.set("")
        self._note_var.set(
            f"공식: {kpi.formula}" + (f"  ·  {kpi.note}" if kpi.note else "")
        )
        self._calc_btn.configure(state="normal")

    def _render_inputs(self, kpi) -> None:
        for w in self._inputs.winfo_children():
            w.destroy()
        self._vars = {}
        for r, (var, label) in enumerate(kpi.inputs):
            ttk.Label(self._inputs, text=label).grid(
                row=r, column=0, sticky="w", pady=2
            )
            sv = tk.StringVar()
            ttk.Entry(self._inputs, textvariable=sv, width=18).grid(
                row=r, column=1, sticky="we", pady=2, padx=(8, 0)
            )
            self._vars[var] = sv
        self._inputs.columnconfigure(1, weight=1)

    # --- compute --------------------------------------------------------
    def _compute(self) -> None:
        if self._current is None:
            return
        try:
            values = {var: _to_float(sv.get()) for var, sv in self._vars.items()}
            result = compute(self._current, values)
        except ValueError as e:
            self._result_var.set(f"오류: {e}")
            return
        text = f"{result:,.4g} {self._current.unit}".strip()
        self._result_var.set(text)
        if self._on_record:
            self._on_record(self._current.key, text, values)

    # --- history reuse --------------------------------------------------
    def load(self, entry) -> None:
        kpi = KPI_BY_KEY.get(entry.expression)
        if kpi is None:
            return
        self._cat.set(kpi.category)
        self._on_category()
        self._metric.set(kpi.name)
        self._on_metric()
        for var, sv in self._vars.items():
            if var in entry.inputs:
                sv.set(str(entry.inputs[var]))

    def on_key(self, event: tk.Event) -> None:
        return
