"""Tkinter view for the unit-conversion mode."""

import tkinter as tk

import ttkbootstrap as ttk

from calc.modes import units as unitmod
from calc.modes.units import CATEGORY_BY_KEY, convert


def _to_float(text: str) -> float:
    text = text.replace(",", "").strip()
    return float(text) if text else 0.0


class UnitView(ttk.Frame):
    def __init__(self, master: tk.Misc, on_record=None) -> None:
        super().__init__(master, padding=10)
        self._on_record = on_record
        self._value_var = tk.StringVar(value="1")
        self._result_var = tk.StringVar(value="")
        self._build()

    def _build(self) -> None:
        top = ttk.Frame(self)
        top.pack(fill="x")
        ttk.Label(top, text="분류").grid(row=0, column=0, sticky="w", padx=(0, 6))
        self._cat = ttk.Combobox(
            top, state="readonly", width=12, values=[c.name for c in unitmod.CATEGORIES]
        )
        self._cat.grid(row=0, column=1, sticky="w")
        self._cat.bind("<<ComboboxSelected>>", lambda e: self._on_category())
        top.columnconfigure(1, weight=1)

        row = ttk.Frame(self, padding=(0, 10))
        row.pack(fill="x")
        ttk.Label(row, text="값").grid(row=0, column=0, sticky="w")
        entry = ttk.Entry(
            row, textvariable=self._value_var, width=14, font=("Helvetica", 14)
        )
        entry.grid(row=0, column=1, sticky="we", padx=6)
        entry.bind("<Return>", lambda e: self._convert())
        self._from = ttk.Combobox(row, state="readonly", width=10)
        self._from.grid(row=0, column=2, padx=2)
        ttk.Button(
            row, text="⇄", width=3, bootstyle="secondary-outline", command=self._swap
        ).grid(row=0, column=3, padx=2)
        self._to = ttk.Combobox(row, state="readonly", width=10)
        self._to.grid(row=0, column=4, padx=2)
        row.columnconfigure(1, weight=1)

        ttk.Button(self, text="환산", bootstyle="primary", command=self._convert).pack(
            fill="x", pady=4
        )
        ttk.Label(
            self,
            textvariable=self._result_var,
            bootstyle="success",
            font=("Helvetica", 20, "bold"),
        ).pack(anchor="w", pady=(6, 0))

        self._cat.current(0)
        self._on_category()

    def _current_category(self):
        for c in unitmod.CATEGORIES:
            if c.name == self._cat.get():
                return c
        return unitmod.CATEGORIES[0]

    def _on_category(self) -> None:
        cat = self._current_category()
        names = cat.unit_names
        self._from.configure(values=names)
        self._to.configure(values=names)
        self._from.current(0)
        self._to.current(1 if len(names) > 1 else 0)
        self._result_var.set("")

    def _swap(self) -> None:
        f, t = self._from.get(), self._to.get()
        self._from.set(t)
        self._to.set(f)
        self._convert()

    def _convert(self) -> None:
        cat = self._current_category()
        try:
            value = _to_float(self._value_var.get())
            result = convert(
                value, cat.unit(self._from.get()), cat.unit(self._to.get())
            )
        except ValueError as e:
            self._result_var.set(f"오류: {e}")
            return
        text = f"{result:,.6g} {self._to.get()}"
        self._result_var.set(text)
        if self._on_record:
            expr = f"{value:g} {self._from.get()} → {self._to.get()}"
            self._on_record(
                expr,
                text,
                {
                    "category": cat.key,
                    "from": self._from.get(),
                    "to": self._to.get(),
                    "value": value,
                },
            )

    def load(self, entry) -> None:
        cat = CATEGORY_BY_KEY.get(entry.inputs.get("category"))
        if cat is None:
            return
        self._cat.set(cat.name)
        self._on_category()
        self._from.set(entry.inputs.get("from", self._from.get()))
        self._to.set(entry.inputs.get("to", self._to.get()))
        self._value_var.set(str(entry.inputs.get("value", "")))
        self._convert()

    def on_key(self, event: tk.Event) -> None:
        return
