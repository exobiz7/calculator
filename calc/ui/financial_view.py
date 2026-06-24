"""Tkinter view for the financial / accounting mode.

Organized as an inner notebook: VAT, margin/discount, TVM, and a loan
amortization table.
"""

import tkinter as tk
from tkinter import ttk

from calc.modes import financial as fin


def _labeled_entry(parent, label, row, default=""):
    ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=2)
    var = tk.StringVar(value=default)
    ttk.Entry(parent, textvariable=var, width=16).grid(
        row=row, column=1, sticky="we", pady=2
    )
    return var


def _to_float(var) -> float:
    text = var.get().replace(",", "").strip()
    return float(text) if text else 0.0


class FinancialView(ttk.Frame):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, padding=6)
        inner = ttk.Notebook(self)
        inner.add(self._vat_tab(inner), text="부가세")
        inner.add(self._margin_tab(inner), text="마진·할인")
        inner.add(self._tvm_tab(inner), text="TVM")
        inner.add(self._amort_tab(inner), text="상환표")
        inner.pack(fill="both", expand=True)

    def on_key(self, event: tk.Event) -> None:  # entries handle their own input
        return

    # --- VAT ------------------------------------------------------------
    def _vat_tab(self, parent):
        f = ttk.Frame(parent, padding=8)
        amount = _labeled_entry(f, "금액", 0)
        rate = _labeled_entry(f, "세율(%)", 1, str(fin.DEFAULT_VAT_RATE))
        result = tk.StringVar(value="")
        ttk.Label(f, textvariable=result, foreground="#0a7").grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(8, 0)
        )

        def show(r):
            result.set(f"공급가 {r.supply:,}  +  세액 {r.vat:,}  =  합계 {r.total:,}")

        ttk.Button(
            f,
            text="공급가 → 합계 (TAX+)",
            command=lambda: show(fin.add_vat(_to_float(amount), _to_float(rate))),
        ).grid(row=2, column=0, columnspan=2, sticky="we", pady=2)
        ttk.Button(
            f,
            text="합계 → 공급가 (TAX−)",
            command=lambda: show(fin.remove_vat(_to_float(amount), _to_float(rate))),
        ).grid(row=3, column=0, columnspan=2, sticky="we", pady=2)
        f.columnconfigure(1, weight=1)
        return f

    # --- margin / discount ---------------------------------------------
    def _margin_tab(self, parent):
        f = ttk.Frame(parent, padding=8)
        cost = _labeled_entry(f, "원가", 0)
        sell = _labeled_entry(f, "판매가", 1)
        rate = _labeled_entry(f, "율(%)", 2)
        result = tk.StringVar(value="")
        ttk.Label(f, textvariable=result, foreground="#0a7", wraplength=240).grid(
            row=7, column=0, columnspan=2, sticky="w", pady=(8, 0)
        )

        ttk.Button(
            f,
            text="판매가 = 원가+마진율",
            command=lambda: result.set(
                f"판매가 {fin.sell_from_cost_margin(_to_float(cost), _to_float(rate)):,}"
            ),
        ).grid(row=3, column=0, columnspan=2, sticky="we", pady=2)
        ttk.Button(
            f,
            text="판매가 = 원가+마크업율",
            command=lambda: result.set(
                f"판매가 {fin.sell_from_cost_markup(_to_float(cost), _to_float(rate)):,}"
            ),
        ).grid(row=4, column=0, columnspan=2, sticky="we", pady=2)
        ttk.Button(
            f,
            text="마진율 (원가,판매가)",
            command=lambda: result.set(
                f"마진율 {fin.margin_rate(_to_float(cost), _to_float(sell)):.2f}%  /  "
                f"마크업율 {fin.markup_rate(_to_float(cost), _to_float(sell)):.2f}%"
            ),
        ).grid(row=5, column=0, columnspan=2, sticky="we", pady=2)
        ttk.Button(
            f,
            text="할인가 (판매가 − 율%)",
            command=lambda: result.set(
                f"할인가 {fin.apply_discount(_to_float(sell), _to_float(rate)):,}"
            ),
        ).grid(row=6, column=0, columnspan=2, sticky="we", pady=2)
        f.columnconfigure(1, weight=1)
        return f

    # --- TVM ------------------------------------------------------------
    def _tvm_tab(self, parent):
        f = ttk.Frame(parent, padding=8)
        n = _labeled_entry(f, "n (기간)", 0)
        i = _labeled_entry(f, "i (%/기간)", 1)
        pv = _labeled_entry(f, "PV", 2)
        pmt = _labeled_entry(f, "PMT", 3)
        fv = _labeled_entry(f, "FV", 4)
        result = tk.StringVar(value="부호 규약: 유출(-) / 유입(+)")
        ttk.Label(f, textvariable=result, foreground="#0a7", wraplength=240).grid(
            row=7, column=0, columnspan=3, sticky="w", pady=(8, 0)
        )

        def solve(target):
            try:
                if target == "FV":
                    val = fin.tvm_fv(
                        _to_float(n), _to_float(i), _to_float(pv), _to_float(pmt)
                    )
                    fv.set(f"{val:.2f}")
                elif target == "PV":
                    val = fin.tvm_pv(
                        _to_float(n), _to_float(i), _to_float(pmt), _to_float(fv)
                    )
                    pv.set(f"{val:.2f}")
                elif target == "PMT":
                    val = fin.tvm_pmt(
                        _to_float(n), _to_float(i), _to_float(pv), _to_float(fv)
                    )
                    pmt.set(f"{val:.2f}")
                elif target == "n":
                    val = fin.tvm_n(
                        _to_float(i), _to_float(pv), _to_float(pmt), _to_float(fv)
                    )
                    n.set(f"{val:.4f}")
                else:  # i
                    val = fin.tvm_rate(
                        _to_float(n), _to_float(pv), _to_float(pmt), _to_float(fv)
                    )
                    i.set(f"{val:.6f}")
                result.set(f"{target} = {val:,.4f}")
            except ValueError as e:
                result.set(f"오류: {e}")

        for c, t in enumerate(["n", "i", "PV", "PMT", "FV"]):
            ttk.Button(f, text=f"{t} 계산", command=lambda t=t: solve(t)).grid(
                row=5 + c // 3, column=c % 3, sticky="we", pady=2, padx=1
            )
        f.columnconfigure(1, weight=1)
        return f

    # --- amortization ---------------------------------------------------
    def _amort_tab(self, parent):
        f = ttk.Frame(parent, padding=8)
        principal = _labeled_entry(f, "원금", 0)
        rate = _labeled_entry(f, "연이율(%)", 1)
        months = _labeled_entry(f, "개월", 2)
        summary = tk.StringVar(value="")
        ttk.Label(f, textvariable=summary, foreground="#0a7").grid(
            row=4, column=0, columnspan=2, sticky="w"
        )

        cols = ("기간", "납입금", "이자", "원금", "잔액")
        tree = ttk.Treeview(f, columns=cols, show="headings", height=8)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=72, anchor="e")
        tree.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=(6, 0))

        def compute():
            for item in tree.get_children():
                tree.delete(item)
            try:
                rows = fin.amortization_schedule(
                    _to_float(principal), _to_float(rate), int(_to_float(months))
                )
            except (ValueError, TypeError) as e:
                summary.set(f"오류: {e}")
                return
            total_interest = sum(r.interest for r in rows)
            for r in rows:
                tree.insert(
                    "",
                    "end",
                    values=(
                        r.period,
                        f"{r.payment:,}",
                        f"{r.interest:,}",
                        f"{r.principal:,}",
                        f"{r.balance:,}",
                    ),
                )
            summary.set(f"월 납입금 {rows[0].payment:,}   총이자 {total_interest:,}")

        ttk.Button(f, text="상환표 계산", command=compute).grid(
            row=3, column=0, columnspan=2, sticky="we", pady=4
        )
        f.columnconfigure(1, weight=1)
        f.rowconfigure(5, weight=1)
        return f
